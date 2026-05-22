"""Batch processing example - Scan multiple domains."""

from reconforge.batch import BatchProcessor

# Create batch processor
processor = BatchProcessor(output_dir="batch_results")

# Example 1: Scan multiple domains
print("Batch Scan Example")
print("=" * 60)

domains = [
    "example.com",
    "example.org",
    "example.net",
]

print(f"\nScanning {len(domains)} domains...")
results = processor.scan_domains(
    domains,
    output_file="batch_results.json",
    concurrent=True,
)

# Print summary
print("\nBatch Scan Summary:")
print("-" * 60)
summary = processor.generate_summary(results)
print(summary)

# Example 2: Scan from file
print("\n\nScanning from file example:")
print("=" * 60)

# Create a sample domains file
with open("domains.txt", "w") as f:
    f.write("example.com\n")
    f.write("example.org\n")
    f.write("example.net\n")

print("\nScanning domains from domains.txt...")
results = processor.scan_from_file(
    "domains.txt",
    output_file="batch_results_from_file.json",
    concurrent=True,
)

print("\nBatch Scan Summary:")
print("-" * 60)
summary = processor.generate_summary(results)
print(summary)

print("\nBatch processing complete!")
print("Results saved to batch_results/ directory")
