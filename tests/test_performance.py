"""
Performance testing script for WATCHDOG
Tests system performance under high network load
"""

import os
import sys
import time

import psutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ml.feature_extractor import FeatureExtractor


class PerformanceTester:
    """Test system performance under load"""

    def __init__(self):
        self.extractor = FeatureExtractor()
        self.results = {}

    def test_feature_extraction_speed(self, iterations=1000):
        """Test feature extraction performance"""
        print(f"\n=== Feature Extraction Performance Test ({iterations} iterations) ===")

        # Sample packet
        packet = {
            "src_ip": "192.168.1.1",
            "dst_ip": "10.0.0.1",
            "protocol": 6,
            "length": 100,
            "flags": "S",
            "dst_port": 80,
            "direction": "outbound",
        }

        start_time = time.time()

        for _i in range(iterations):
            features = self.extractor.extract_packet_features(packet)
            selected, _ = self.extractor.get_selected_features(features)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = (total_time / iterations) * 1000  # Convert to ms
        throughput = iterations / total_time  # packets per second

        self.results["feature_extraction"] = {
            "total_time": total_time,
            "avg_time_ms": avg_time,
            "throughput_pps": throughput,
        }

        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per packet: {avg_time:.3f}ms")
        print(f"Throughput: {throughput:.0f} packets/second")

        # Performance criteria
        if avg_time < 1.0:
            print("PASS: Average time < 1ms")
        else:
            print("WARNING: Average time >= 1ms")

        return avg_time < 1.0

    def test_memory_usage(self, duration=10):
        """Test memory usage over time"""
        print(f"\n=== Memory Usage Test ({duration}s duration) ===")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory: {initial_memory:.2f} MB")

        # Simulate continuous packet processing
        start_time = time.time()
        packet_count = 0

        while time.time() - start_time < duration:
            packet = {
                "src_ip": f"192.168.1.{packet_count % 255}",
                "dst_ip": f"10.0.0.{packet_count % 255}",
                "protocol": 6,
                "length": 100 + (packet_count % 500),
                "flags": "S",
                "dst_port": 80,
                "direction": "outbound",
            }

            features = self.extractor.extract_packet_features(packet)
            selected, _ = self.extractor.get_selected_features(features)
            packet_count += 1

            # Small delay to simulate real-time processing
            time.sleep(0.001)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        self.results["memory_usage"] = {
            "initial_mb": initial_memory,
            "final_mb": final_memory,
            "increase_mb": memory_increase,
            "packets_processed": packet_count,
        }

        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"Packets processed: {packet_count}")

        # Performance criteria
        if memory_increase < 100:
            print("PASS: Memory increase < 100MB")
        else:
            print("WARNING: Memory increase >= 100MB")

        return memory_increase < 100

    def test_cpu_usage(self, duration=10):
        """Test CPU usage under load"""
        print(f"\n=== CPU Usage Test ({duration}s duration) ===")

        process = psutil.Process()
        cpu_samples = []

        start_time = time.time()
        packet_count = 0

        while time.time() - start_time < duration:
            packet = {
                "src_ip": f"192.168.1.{packet_count % 255}",
                "dst_ip": f"10.0.0.{packet_count % 255}",
                "protocol": 6,
                "length": 100 + (packet_count % 500),
                "flags": "S",
                "dst_port": 80,
                "direction": "outbound",
            }

            features = self.extractor.extract_packet_features(packet)
            selected, _ = self.extractor.get_selected_features(features)
            packet_count += 1

            # Sample CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            cpu_samples.append(cpu_percent)

            time.sleep(0.001)

        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)

        self.results["cpu_usage"] = {
            "avg_cpu_percent": avg_cpu,
            "max_cpu_percent": max_cpu,
            "packets_processed": packet_count,
        }

        print(f"Average CPU usage: {avg_cpu:.1f}%")
        print(f"Peak CPU usage: {max_cpu:.1f}%")
        print(f"Packets processed: {packet_count}")

        # Performance criteria
        if avg_cpu < 30:
            print("PASS: Average CPU < 30%")
        else:
            print("WARNING: Average CPU >= 30%")

        return avg_cpu < 30

    def test_high_throughput(self, target_pps=1000, duration=5):
        """Test system under high packet load"""
        print(f"\n=== High Throughput Test (target: {target_pps} pps, {duration}s duration) ===")

        process = psutil.Process()
        start_time = time.time()
        packet_count = 0
        failed_packets = 0

        while time.time() - start_time < duration:
            try:
                packet = {
                    "src_ip": f"192.168.1.{packet_count % 255}",
                    "dst_ip": f"10.0.0.{packet_count % 255}",
                    "protocol": 6,
                    "length": 100 + (packet_count % 500),
                    "flags": "S",
                    "dst_port": 80,
                    "direction": "outbound",
                }

                features = self.extractor.extract_packet_features(packet)
                self.extractor.get_selected_features(features)
                packet_count += 1

                # Calculate required delay to hit target PPS
                elapsed = time.time() - start_time
                target_count = int(target_pps * elapsed)

                if packet_count > target_count:
                    time.sleep(0.0001)  # Small delay to control rate

            except Exception:
                failed_packets += 1

        end_time = time.time()
        actual_duration = end_time - start_time
        actual_pps = packet_count / actual_duration
        final_memory = process.memory_info().rss / 1024 / 1024
        avg_cpu = process.cpu_percent(interval=0.1)

        self.results["high_throughput"] = {
            "target_pps": target_pps,
            "actual_pps": actual_pps,
            "duration": actual_duration,
            "packets_processed": packet_count,
            "failed_packets": failed_packets,
            "final_memory_mb": final_memory,
            "avg_cpu_percent": avg_cpu,
        }

        print(f"Target PPS: {target_pps}")
        print(f"Actual PPS: {actual_pps:.0f}")
        print(f"Packets processed: {packet_count}")
        print(f"Failed packets: {failed_packets}")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Average CPU: {avg_cpu:.1f}%")

        # Performance criteria
        success_rate = (
            (packet_count - failed_packets) / packet_count * 100 if packet_count > 0 else 0
        )

        if actual_pps >= target_pps * 0.9 and success_rate > 99:
            print("PASS: Throughput >= 90% of target, success rate > 99%")
            return True
        else:
            print("WARNING: Throughput or success rate below threshold")
            return False

    def generate_report(self):
        """Generate performance test report"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)

        if "feature_extraction" in self.results:
            print("\nFeature Extraction:")
            print(f"  Throughput: {self.results['feature_extraction']['throughput_pps']:.0f} pps")
            print(f"  Avg time: {self.results['feature_extraction']['avg_time_ms']:.3f} ms")

        if "memory_usage" in self.results:
            print("\nMemory Usage:")
            print(f"  Initial: {self.results['memory_usage']['initial_mb']:.2f} MB")
            print(f"  Final: {self.results['memory_usage']['final_mb']:.2f} MB")
            print(f"  Increase: {self.results['memory_usage']['increase_mb']:.2f} MB")

        if "cpu_usage" in self.results:
            print("\nCPU Usage:")
            print(f"  Average: {self.results['cpu_usage']['avg_cpu_percent']:.1f}%")
            print(f"  Peak: {self.results['cpu_usage']['max_cpu_percent']:.1f}%")

        if "high_throughput" in self.results:
            print("\nHigh Throughput:")
            print(f"  Target: {self.results['high_throughput']['target_pps']} pps")
            print(f"  Actual: {self.results['high_throughput']['actual_pps']:.0f} pps")
            print(
                f"  Success rate: {((self.results['high_throughput']['packets_processed'] - self.results['high_throughput']['failed_packets']) / self.results['high_throughput']['packets_processed'] * 100):.1f}%"
            )

        print("\n" + "=" * 60)


def run_performance_tests():
    """Run all performance tests"""
    print("WATCHDOG Performance Testing")
    print("=" * 60)

    tester = PerformanceTester()

    # Run tests
    results = {}

    try:
        results["feature_extraction"] = tester.test_feature_extraction_speed(iterations=1000)
    except Exception as e:
        print(f"Feature extraction test failed: {e}")
        results["feature_extraction"] = False

    try:
        results["memory"] = tester.test_memory_usage(duration=10)
    except Exception as e:
        print(f"Memory test failed: {e}")
        results["memory"] = False

    try:
        results["cpu"] = tester.test_cpu_usage(duration=10)
    except Exception as e:
        print(f"CPU test failed: {e}")
        results["cpu"] = False

    try:
        results["throughput"] = tester.test_high_throughput(target_pps=1000, duration=5)
    except Exception as e:
        print(f"Throughput test failed: {e}")
        results["throughput"] = False

    # Generate report
    tester.generate_report()

    # Overall result
    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("All performance tests passed!")
        return 0
    else:
        print("Some performance tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_performance_tests())
