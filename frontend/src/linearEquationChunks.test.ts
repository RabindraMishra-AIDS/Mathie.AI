import { describe, expect, it } from "vitest";
import { getPracticeChunk, linearEquationChunks } from "./linearEquationChunks";

describe("linear equation source chunks", () => {
  it("keeps each practice set tied to its registered PDF pages", () => {
    expect(
      linearEquationChunks.map(({ setNumber, pageStart, pageEnd }) => [
        setNumber,
        pageStart,
        pageEnd,
      ]),
    ).toEqual([
      [1, 11, 14],
      [2, 15, 19],
      [3, 20, 26],
      [4, 27, 29],
      [5, 30, 36],
    ]);
  });

  it("returns an isolated chunk for a selected set", () => {
    const chunk = getPracticeChunk(1);

    expect(chunk.pageStart).toBe(11);
    expect(chunk.pageEnd).toBe(14);
    expect(chunk.context).not.toContain("determinants");
  });

  it("provides five static textbook problems for every practice set", () => {
    for (const chunk of linearEquationChunks) {
      expect(chunk.examples).toHaveLength(5);
      expect(chunk.context).not.toHaveLength(0);
    }
  });
});
