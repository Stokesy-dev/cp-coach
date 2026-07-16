import { fetchAllProblems } from './src/services/codeforces';

async function run() {
  try {
    console.log("--- Test 1: Fetching problems (should query API and cache the result) ---");
    const start1 = Date.now();
    const problems1 = await fetchAllProblems();
    const end1 = Date.now();
    console.log(`Fetch 1 completed. Found ${problems1.length} problems. Time taken: ${end1 - start1}ms`);

    console.log("\n--- Test 2: Fetching problems again (should hit in-memory cache) ---");
    const start2 = Date.now();
    const problems2 = await fetchAllProblems();
    const end2 = Date.now();
    console.log(`Fetch 2 completed. Found ${problems2.length} problems. Time taken: ${end2 - start2}ms`);
    
    if (end2 - start2 < 10) {
      console.log("\n✅ Cache verified! The second fetch was near-instantaneous.");
    } else {
      console.log("\n❌ Cache failed! The second fetch took too long.");
    }
  } catch (err) {
    console.error("Error during verification:", err);
  }
}
run();
