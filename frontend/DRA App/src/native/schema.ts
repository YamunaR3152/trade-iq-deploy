import type { OverallScoreSummary, WeeklyScore } from "./types";

export const studentProfileFields = [
  "Student ID",
  "Full Name",
  "Age",
  "Date of Birth",
  "Email",
  "Phone Number",
  "University",
  "Course",
  "Year of Study",
  "Participation Type",
  "Team Name",
] as const;

export const portfolioSetupFields = ["Student ID", "Total Capital", "Risk Appetite", "Investment Horizon", "Competition Round"] as const;

export const tradeLogFields = [
  "Trade ID",
  "Student ID",
  "Added By (Teams)",
  "Trade Date",
  "Stock Ticker",
  "Stock Name",
  "Sector",
  "Allocation %",
  "Amount Invested",
  "Buy Price",
  "Current / Sell Price",
  "Trade Type",
  "Tag 1",
  "Tag 2",
  "Tag 3",
  "Thesis",
] as const;

export const weeklyScoreFields = [
  "Student ID",
  "Week Number",
  "Total Return Score",
  "Benchmark Return Score",
  "Net Profit Margin Score",
  "Sharpe Ratio Score",
  "Max Drawdown Score",
  "Portfolio Beta Score",
  "Diversification Score",
  "Trade Consistency Score",
  "Prediction Accuracy Score",
  "Trade Execution Score",
  "AI Thesis Score",
  "Weekly Total Score",
  "Weekly Rank",
] as const;

export const overallSummaryFields = [
  "Student ID",
  "Week 1 Total",
  "Week 2 Total",
  "Week 3 Total",
  "Week 4 Total",
  "Cumulative Score",
  "Report Score (Manual)",
  "Final Score",
  "Overall Rank",
] as const;

export const sampleWeeklyScores = (studentId: string): WeeklyScore[] => [
  {
    studentId,
    weekNumber: "1",
    totalReturnScore: 21,
    benchmarkReturnScore: 13,
    netProfitMarginScore: 8,
    sharpeRatioScore: 6,
    maxDrawdownScore: 6,
    portfolioBetaScore: 5,
    diversificationScore: 5,
    tradeConsistencyScore: 4,
    predictionAccuracyScore: 3,
    tradeExecutionScore: 8,
    aiThesisScore: 4,
    weeklyTotalScore: 82,
    weeklyRank: 14,
  },
  {
    studentId,
    weekNumber: "2",
    totalReturnScore: 19,
    benchmarkReturnScore: 12,
    netProfitMarginScore: 8,
    sharpeRatioScore: 5,
    maxDrawdownScore: 6,
    portfolioBetaScore: 5,
    diversificationScore: 6,
    tradeConsistencyScore: 4,
    predictionAccuracyScore: 3,
    tradeExecutionScore: 8,
    aiThesisScore: 4,
    weeklyTotalScore: 77,
    weeklyRank: 19,
  },
  {
    studentId,
    weekNumber: "3",
    totalReturnScore: 20,
    benchmarkReturnScore: 13,
    netProfitMarginScore: 8,
    sharpeRatioScore: 6,
    maxDrawdownScore: 6,
    portfolioBetaScore: 5,
    diversificationScore: 6,
    tradeConsistencyScore: 4,
    predictionAccuracyScore: 4,
    tradeExecutionScore: 9,
    aiThesisScore: 4,
    weeklyTotalScore: 80,
    weeklyRank: 16,
  },
  {
    studentId,
    weekNumber: "4",
    totalReturnScore: 0,
    benchmarkReturnScore: 0,
    netProfitMarginScore: 0,
    sharpeRatioScore: 0,
    maxDrawdownScore: 0,
    portfolioBetaScore: 0,
    diversificationScore: 0,
    tradeConsistencyScore: 0,
    predictionAccuracyScore: 0,
    tradeExecutionScore: 0,
    aiThesisScore: 0,
    weeklyTotalScore: 0,
    weeklyRank: 0,
  },
];

export const sampleOverallSummary = (studentId: string): OverallScoreSummary => {
  const weekly = sampleWeeklyScores(studentId);
  const cumulativeScore = weekly.reduce((sum, item) => sum + item.weeklyTotalScore, 0);
  const reportScoreManual = 4;
  return {
    studentId,
    week1Total: weekly[0].weeklyTotalScore,
    week2Total: weekly[1].weeklyTotalScore,
    week3Total: weekly[2].weeklyTotalScore,
    week4Total: weekly[3].weeklyTotalScore,
    cumulativeScore,
    reportScoreManual,
    finalScore: cumulativeScore + reportScoreManual,
    overallRank: 14,
  };
};
