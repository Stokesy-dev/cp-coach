import { fetchAllProblems } from './src/services/codeforces';

async function run() {
  try {
    const problems = await fetchAllProblems();
    console.log("Fetched", problems.length, "problems");
    console.log("Sample:", problems[0]);
  } catch (err) {
    console.error(err);
  }
}
run();
