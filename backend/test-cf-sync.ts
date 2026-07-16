import { fetchUserSubmissions } from './src/services/codeforces';

async function run() {
  try {
    const handle = 'tourist';
    console.log(`--- Test 1: Fetching submissions for '${handle}' (should query API and cache) ---`);
    const start1 = Date.now();
    const subs1 = await fetchUserSubmissions(handle);
    const end1 = Date.now();
    console.log(`Fetch 1 completed. Found ${subs1.length} submissions. Time taken: ${end1 - start1}ms`);

    console.log(`\n--- Test 2: Fetching submissions for '${handle}' again (should hit cache) ---`);
    const start2 = Date.now();
    const subs2 = await fetchUserSubmissions(handle);
    const end2 = Date.now();
    console.log(`Fetch 2 completed. Found ${subs2.length} submissions. Time taken: ${end2 - start2}ms`);

    console.log(`\n--- Test 3: Fetching with case variation '${handle.toUpperCase()}' (should be case-insensitive and hit cache) ---`);
    const start3 = Date.now();
    const subs3 = await fetchUserSubmissions(handle.toUpperCase());
    const end3 = Date.now();
    console.log(`Fetch 3 completed. Found ${subs3.length} submissions. Time taken: ${end3 - start3}ms`);

    if (end2 - start2 < 10 && end3 - start3 < 10) {
      console.log("\n✅ Submissions cache verified! Subsequent fetches were near-instantaneous and case-insensitive.");
    } else {
      console.log("\n❌ Cache failed!");
    }
  } catch (err) {
    console.error("Error during verification:", err);
  }
}
run();
