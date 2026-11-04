export type PracticeChunk = {
  setNumber: number;
  pageStart: number;
  pageEnd: number;
  topics: string[];
  context: string;
  examples: string[];
};

export const linearEquationChunks: PracticeChunk[] = [
  {
    setNumber: 1,
    pageStart: 11,
    pageEnd: 14,
    topics: ["linear equations", "simultaneous equations", "elimination"],
    context:
      "General form: ax + by + c = 0, where a and b are not both zero. For simultaneous equations, eliminate one variable by making its coefficients opposites, or write one variable in terms of the other and substitute.",
    examples: [
      "Decide whether 4m + 3n = 12 is a linear equation in two variables.",
      "Decide whether 3x² - 7y = 13 is a linear equation in two variables.",
      "Solve: 5x - 3y = 8 and 3x + y = 2.",
      "Solve: 3x + 2y = 29 and 5x - y = 18.",
      "Solve: 15x + 17y = 21 and 17x + 15y = 11.",
    ],
  },
  {
    setNumber: 2,
    pageStart: 15,
    pageEnd: 19,
    topics: ["linear graphs", "ordered pairs", "graphical method"],
    context:
      "A graph of a linear equation in two variables is a straight line. An ordered pair satisfying the equation represents a point on that line. The point of intersection of two lines is the solution of the simultaneous equations.",
    examples: [
      "Solve: 3a + 5b = 26 and a + 5b = 22.",
      "Solve: x + 7y = 10 and 3x - 2y = 7.",
      "Complete an ordered-pair table and draw the graph of x + y = 3.",
      "Complete an ordered-pair table and draw the graph of x - y = 4.",
      "Solve graphically: x + y = 6 and x - y = 4.",
    ],
  },
  {
    setNumber: 3,
    pageStart: 20,
    pageEnd: 26,
    topics: ["determinants", "Cramer's rule", "simultaneous equations"],
    context:
      "For a determinant |a b; c d|, its value is ad - bc. Write equations as a₁x + b₁y = c₁ and a₂x + b₂y = c₂. Then D = |a₁ b₁; a₂ b₂|, Dx = |c₁ b₁; c₂ b₂|, Dy = |a₁ c₁; a₂ c₂|, x = Dx/D, and y = Dy/D.",
    examples: [
      "Find the value of determinant |5  3; 7  9|.",
      "Find the value of determinant |-8  -3; 2  4|.",
      "Solve using Cramer's rule: 5x + 3y = -11 and 2x + 4y = -10.",
      "Solve using Cramer's rule: 2x + y = 19 and 2x - 3y = -3.",
      "Solve using Cramer's rule: 3x - 4y = 10 and 4x + 3y = 5.",
    ],
  },
  {
    setNumber: 4,
    pageStart: 27,
    pageEnd: 29,
    topics: ["equations reducible to linear form", "substitution"],
    context:
      "Create new variables by replacing repeated expressions, then solve the resulting linear equations. For fractions, the denominator cannot be zero. In the source examples, m = 1/x and n = 1/y, or a = 1/(x - y) and b = 1/(x + y).",
    examples: [
      "Solve by substitution: 4/x + 5/y = 7 and 3/x + 4/y = 5.",
      "Using m = 1/x and n = 1/y, solve 4m + 5n = 7 and 3m + 4n = 5, then return to x and y.",
      "Solve by substitution: 4/(x - y) + 1/(x + y) = 3 and 2/(x - y) - 3/(x + y) = 5.",
      "Using a = 1/(x - y) and b = 1/(x + y), solve 4a + b = 3 and 2a - 3b = 5, then return to x and y.",
      "Use m = 1/(x - 5) and n = 1/(2y - 4) to reduce the source activity to linear equations.",
    ],
  },
  {
    setNumber: 5,
    pageStart: 30,
    pageEnd: 36,
    topics: ["applications", "word problems", "simultaneous equations"],
    context:
      "Define the unknown quantities first, translate each condition into one equation, solve the pair, and interpret the variables in the stated situation. For a rectangle with length x and breadth y, the source uses 2(x + y) for the perimeter.",
    examples: [
      "Two numbers differ by 3. The sum of twice the smaller number and thrice the greater number is 19. Find the numbers.",
      "The sum of a father's age and twice his son's age is 70. Twice the father's age plus the son's age is 95. Find their present ages.",
      "The denominator of a fraction is 4 more than twice its numerator. It becomes 12 times the numerator when both numerator and denominator are reduced by 6. Find the fraction.",
      "A 10-ton truck is fully loaded by 150 boxes of type A and 100 boxes of type B; it is also full with 260 boxes of A and 40 boxes of B. Find the weight of each box type.",
      "Of a 1900 km journey, Vishal travelled by bus at 60 km/hr and aeroplane at 700 km/hr in 5 hours. Find the distance travelled by bus.",
    ],
  },
];

export function getPracticeChunk(setNumber: number): PracticeChunk {
  const chunk = linearEquationChunks.find((item) => item.setNumber === setNumber);
  if (!chunk) {
    throw new Error(`No textbook chunk exists for practice set ${setNumber}.`);
  }
  return chunk;
}
