import { Text, View } from "react-native";
import { C, font } from "../constants";
import { sampleOverallSummary, sampleWeeklyScores } from "../schema";
import { GlassCard, Progress, SectionTitle } from "../components/ui";

function Row({ label, value, color = C.text1 }: { label: string; value: string; color?: string }) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", gap: 12, paddingVertical: 9, borderBottomColor: C.border, borderBottomWidth: 1 }}>
      <Text selectable style={{ color: C.text2, fontSize: 12, flex: 1 }}>
        {label}
      </Text>
      <Text selectable style={{ color, fontFamily: font.mono, fontSize: 12 }}>
        {value}
      </Text>
    </View>
  );
}

export function Scores({ studentId }: { studentId: string }) {
  const weeklyScores = sampleWeeklyScores(studentId);
  const summary = sampleOverallSummary(studentId);

  return (
    <View style={{ gap: 16 }}>
      <View>
        <Text selectable style={{ color: C.text0, fontFamily: font.medium, fontSize: 25 }}>
          Scores
        </Text>
        <Text selectable style={{ color: C.text2, fontSize: 13, marginTop: 4 }}>
          Weekly Scores: one entry per student per week.
        </Text>
      </View>

      <GlassCard style={{ padding: 16, gap: 12 }} accent={C.green}>
        <SectionTitle title="Weekly Scores" accent={C.green} />
        {weeklyScores.map((week) => (
          <View key={week.weekNumber} style={{ padding: 12, borderRadius: 12, backgroundColor: C.bg2, borderColor: C.border, borderWidth: 1, gap: 8 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <Text selectable style={{ color: C.text0, fontFamily: font.medium, fontSize: 14 }}>
                Week {week.weekNumber}
              </Text>
              <Text selectable style={{ color: week.weeklyTotalScore ? C.green : C.text2, fontFamily: font.mono, fontSize: 15 }}>
                {week.weeklyTotalScore}/100
              </Text>
            </View>
            <Progress label="Total Return Score" value={week.totalReturnScore * 4} color={C.green} />
            <Progress label="Benchmark Return Score" value={Math.round((week.benchmarkReturnScore / 15) * 100)} color={C.cyan} />
            <Progress label="Trade Execution Score" value={week.tradeExecutionScore * 10} color={C.gold} />
            <Row label="Weekly Rank" value={week.weeklyRank ? `#${week.weeklyRank}` : "Pending"} color={week.weeklyRank ? C.cyan : C.text2} />
          </View>
        ))}
      </GlassCard>

      <GlassCard style={{ padding: 16, gap: 10 }} accent={C.purple}>
        <SectionTitle title="Overall Summary" accent={C.purple} />
        <Row label="User ID" value={summary.studentId} color={C.cyan} />
        <Row label="Week 1 Total" value={`${summary.week1Total}/100`} />
        <Row label="Week 2 Total" value={`${summary.week2Total}/100`} />
        <Row label="Week 3 Total" value={`${summary.week3Total}/100`} />
        <Row label="Week 4 Total" value={`${summary.week4Total}/100`} />
        <Row label="Cumulative Score" value={`${summary.cumulativeScore}/400`} color={C.green} />
        <Row label="Report Score (Manual)" value={`${summary.reportScoreManual}/5`} />
        <Row label="Final Score" value={`${summary.finalScore}/405`} color={C.gold} />
        <Row label="Overall Rank" value={`#${summary.overallRank}`} color={C.cyan} />
      </GlassCard>
    </View>
  );
}
