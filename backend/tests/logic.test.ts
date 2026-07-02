import { calculateWeaknessScore } from '../src/services/weakness';
import { calculateInitialTargetRating, adjustTargetRating, getRatingBands } from '../src/services/rating';

describe('Weakness Score', () => {
  it('should return 0 when attempted is 0', () => {
    expect(calculateWeaknessScore(0, 0)).toBe(0);
  });

  it('should calculate weakness score correctly', () => {
    const W = calculateWeaknessScore(3, 1);
    expect(W).toBeCloseTo((2 / 3) * Math.log(4));
  });

  it('ranks correctly (DP vs Math)', () => {
    const W_DP = calculateWeaknessScore(10, 2);
    const W_Math = calculateWeaknessScore(1, 0);
    expect(W_DP).toBeGreaterThan(W_Math);
  });
});

describe('Target Rating', () => {
  it('calculates initial target rating from tag ratings', () => {
    expect(calculateInitialTargetRating([1100, 1300, 1500], [])).toBe(1400);
  });

  it('calculates initial target rating from overall ratings if tag is empty', () => {
    expect(calculateInitialTargetRating([], [1200, 1400])).toBe(1400);
  });

  it('rounds to nearest 100', () => {
    expect(calculateInitialTargetRating([1250], [])).toBe(1400);
    expect(calculateInitialTargetRating([1240], [])).toBe(1300);
  });

  it('defaults to 800 + 100 = 900 if no solves at all', () => {
    expect(calculateInitialTargetRating([], [])).toBe(900);
  });

  it('adjusts target rating based on pass/fail', () => {
    expect(adjustTargetRating(1200, 'pass')).toBe(1300);
    expect(adjustTargetRating(1200, 'fail')).toBe(1100);
  });

  it('clamps minimum target rating to 800 on fail', () => {
    expect(adjustTargetRating(800, 'fail')).toBe(800);
  });
});

describe('Rating Bands Widening', () => {
  it('generates correct sequence of bands', () => {
    const bands = getRatingBands(1200);
    expect(bands[0]).toEqual({ min: 1200, max: 1200 });
    expect(bands[1]).toEqual({ min: 1100, max: 1300 });
    expect(bands[bands.length - 1]).toEqual({ min: 800, max: 2200 });
  });

  it('clamps min correctly at high offset', () => {
    const bands = getRatingBands(1000);
    const lastBand = bands[bands.length - 1];
    expect(lastBand.min).toBe(800);
    expect(lastBand.max).toBe(2000);
  });
});
