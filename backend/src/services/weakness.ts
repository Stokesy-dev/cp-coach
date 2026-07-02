export function calculateWeaknessScore(attempted: number, solved: number): number {
  if (attempted === 0) {
    return 0;
  }
  const solveRate = solved / attempted;
  const W = (1 - solveRate) * Math.log(1 + attempted);
  return W;
}
