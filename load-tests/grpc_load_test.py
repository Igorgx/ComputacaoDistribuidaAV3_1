from __future__ import annotations

import argparse
import csv
import random
import statistics
import threading
import time
from collections import defaultdict
from pathlib import Path

import grpc

from python.grpc.generated import music_pb2, music_pb2_grpc


TASKS = (
    ("grpc:listMusics", 4),
    ("grpc:getUser", 2),
    ("grpc:createPlaylist", 2),
    ("grpc:musicsByPlaylist", 3),
    ("grpc:playlistsByMusic", 2),
)


class Metrics:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.times: dict[str, list[float]] = defaultdict(list)
        self.failures: dict[str, int] = defaultdict(int)

    def record(self, name: str, elapsed_ms: float, failed: bool) -> None:
        with self.lock:
            self.times[name].append(elapsed_ms)
            if failed:
                self.failures[name] += 1


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((percent / 100) * (len(ordered) - 1))))
    return ordered[index]


def worker(target: str, deadline: float, metrics: Metrics) -> None:
    channel = grpc.insecure_channel(target)
    users = music_pb2_grpc.UserServiceStub(channel)
    musics = music_pb2_grpc.MusicServiceStub(channel)
    playlists = music_pb2_grpc.PlaylistServiceStub(channel)
    task_names = [name for name, weight in TASKS for _ in range(weight)]

    try:
        while time.perf_counter() < deadline:
            name = random.choice(task_names)
            started = time.perf_counter()
            failed = False
            try:
                if name == "grpc:listMusics":
                    musics.ListMusics(music_pb2.Empty())
                elif name == "grpc:getUser":
                    users.GetUser(music_pb2.IdRequest(id=random.randint(1, 250)))
                elif name == "grpc:createPlaylist":
                    playlist = music_pb2.Playlist(
                        name=f"Carga {random.randint(100000, 999999)}",
                        user_id=random.randint(1, 250),
                        music_ids=[random.randint(1, 500) for _ in range(5)],
                    )
                    playlists.CreatePlaylist(music_pb2.PlaylistRequest(playlist=playlist))
                elif name == "grpc:musicsByPlaylist":
                    playlists.ListMusicsByPlaylist(
                        music_pb2.IdRequest(id=random.randint(1, 400))
                    )
                else:
                    playlists.ListPlaylistsByMusic(
                        music_pb2.IdRequest(id=random.randint(1, 500))
                    )
            except Exception:
                failed = True
            metrics.record(name, (time.perf_counter() - started) * 1000, failed)
            time.sleep(random.uniform(0.1, 0.8))
    finally:
        channel.close()


def row(name: str, values: list[float], failures: int, elapsed: float) -> dict[str, str]:
    count = len(values)
    return {
        "Type": "grpc",
        "Name": name,
        "Request Count": str(count),
        "Failure Count": str(failures),
        "Median Response Time": f"{statistics.median(values) if values else 0:.2f}",
        "Average Response Time": f"{statistics.mean(values) if values else 0:.2f}",
        "Min Response Time": f"{min(values) if values else 0:.2f}",
        "Max Response Time": f"{max(values) if values else 0:.2f}",
        "Average Content Size": "0",
        "Requests/s": f"{count / elapsed if elapsed > 0 else 0:.2f}",
        "Failures/s": f"{failures / elapsed if elapsed > 0 else 0:.2f}",
        "50%": f"{percentile(values, 50):.2f}",
        "66%": f"{percentile(values, 66):.2f}",
        "75%": f"{percentile(values, 75):.2f}",
        "80%": f"{percentile(values, 80):.2f}",
        "90%": f"{percentile(values, 90):.2f}",
        "95%": f"{percentile(values, 95):.2f}",
        "98%": f"{percentile(values, 98):.2f}",
        "99%": f"{percentile(values, 99):.2f}",
        "99.9%": f"{percentile(values, 99.9):.2f}",
        "99.99%": f"{percentile(values, 99.99):.2f}",
        "100%": f"{percentile(values, 100):.2f}",
    }


def write_csv(out: Path, metrics: Metrics, elapsed: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "Type",
        "Name",
        "Request Count",
        "Failure Count",
        "Median Response Time",
        "Average Response Time",
        "Min Response Time",
        "Max Response Time",
        "Average Content Size",
        "Requests/s",
        "Failures/s",
        "50%",
        "66%",
        "75%",
        "80%",
        "90%",
        "95%",
        "98%",
        "99%",
        "99.9%",
        "99.99%",
        "100%",
    ]
    rows = []
    all_values: list[float] = []
    total_failures = 0
    for name in sorted(metrics.times):
        values = metrics.times[name]
        failures = metrics.failures[name]
        all_values.extend(values)
        total_failures += failures
        rows.append(row(name, values, failures, elapsed))
    aggregate = row("Aggregated", all_values, total_failures, elapsed)
    aggregate["Type"] = ""
    rows.append(aggregate)

    with out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Threaded gRPC load test")
    parser.add_argument("--target", required=True, help="host:port, e.g. 127.0.0.1:8102")
    parser.add_argument("--users", type=int, required=True)
    parser.add_argument("--spawn-rate", type=float, required=True)
    parser.add_argument("--run-time", type=int, required=True, help="seconds")
    parser.add_argument("--out", required=True, help="output prefix in report/results")
    args = parser.parse_args()

    metrics = Metrics()
    started = time.perf_counter()
    deadline = started + args.run_time
    threads: list[threading.Thread] = []

    print(
        f"Starting gRPC load: target={args.target}, users={args.users}, "
        f"spawn_rate={args.spawn_rate}/s, run_time={args.run_time}s"
    )
    for _ in range(args.users):
        thread = threading.Thread(target=worker, args=(args.target, deadline, metrics))
        thread.start()
        threads.append(thread)
        time.sleep(1 / args.spawn_rate)

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - started
    out = Path("report/results") / f"{args.out}_stats.csv"
    write_csv(out, metrics, elapsed)

    all_values = [value for values in metrics.times.values() for value in values]
    total_requests = len(all_values)
    total_failures = sum(metrics.failures.values())
    failure_rate = (total_failures / total_requests * 100) if total_requests else 0
    print("Aggregated")
    print(f"Requests: {total_requests}")
    print(f"Failures: {total_failures} ({failure_rate:.2f}%)")
    print(f"Requests/s: {total_requests / elapsed if elapsed > 0 else 0:.2f}")
    print(f"Average Response Time: {statistics.mean(all_values) if all_values else 0:.2f} ms")
    print(f"95%: {percentile(all_values, 95):.2f} ms")
    print(f"CSV: {out}")


if __name__ == "__main__":
    main()
