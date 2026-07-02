export function calculateInitialTargetRating(
  tagSolvedRatings: number[],
  overallSolvedRatings: number[]
): number {
  let baseline = 800;

  if (tagSolvedRatings.length > 0) {
    const sum = tagSolvedRatings.reduce((a, b) => a + b, 0);
    const avg = sum / tagSolvedRatings.length;
    // Round to nearest 100
    baseline = Math.round(avg / 100) * 100;
  } else if (overallSolvedRatings.length > 0) {
    const sum = overallSolvedRatings.reduce((a, b) => a + b, 0);
    const avg = sum / overallSolvedRatings.length;
    baseline = Math.round(avg / 100) * 100;
  }

  return baseline + 100;
}

export function adjustTargetRating(currentRating: number, result: "pass" | "fail"): number {
  if (result === "pass") {
    return currentRating + 100;
  } else {
    return Math.max(800, currentRating - 100);
  }
}

export function getRatingBands(targetRating: number): { min: number; max: number }[] {
  const bands = [];
  bands.push({ min: targetRating, max: targetRating });

  for (let offset = 100; offset <= 1000; offset += 100) {
    bands.push({
      min: Math.max(800, targetRating - offset),
      max: targetRating + offset
    });
  }
  
  return bands;
}
