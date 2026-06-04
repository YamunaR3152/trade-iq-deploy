import { TrendingDown, TrendingUp } from "lucide-react-native";
import { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { C, font } from "../constants";
import { sampleOverallSummary } from "../schema";
import { Legend, LineChart } from "../components/charts";
import { GlassCard, Progress, SectionTitle } from "../components/ui";

function StatCard({ label, value, sub, color = C.cyan }: { label: string; value: string; sub: string; color?: string }) {
  return (
    <GlassCard style={{ flex: 1, minWidth: 150, padding: 14 }} accent={color}>
      <SectionTitle title={label} accent={color} />
      <Text selectable style={{ color: C.text0, fontFamily: font.mono, fontSize: 24, marginTop: 5 }}>
        {value}
      </Text>
      <Text selectable style={{ color, fontFamily: font.regular, fontSize: 11, marginTop: 4 }}>
        {sub}
      </Text>
    </GlassCard>
  );
}

export function Dashboard({ userName, studentId }: { userName: string; studentId: string }) {
  const [tab, setTab] = useState<"overview" | "scoring" | "market" | "tasks">("overview");
  const tabs = ["overview", "scoring", "market", "tasks"] as const;
  const summary = sampleOverallSummary(studentId);

  return (
    <View style={{ gap: 16 }}>
      <View>
        <Text selectable style={{ color: C.text0, fontFamily: font.medium, fontSize: 25 }}>
          Welcome, {userName.split(" ")[0] || "Analyst"}
        </Text>
        <Text selectable style={{ color: C.text2, fontFamily: font.regular, fontSize: 13, marginTop: 4 }}>
          Your portfolio is tracking <Text style={{ color: C.green }}>+6.2%</Text> above benchmark this week.
        </Text>
      </View>

      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
        <StatCard label="Portfolio Value" value="$10,620" sub="+6.2% vs base" color={C.green} />
        <StatCard label="Final Score" value={String(summary.finalScore)} sub="out of 405" color={C.cyan} />
        <StatCard label="Leaderboard" value={`#${summary.overallRank}`} sub="of 312 students" color={C.purple} />
        <StatCard label="Strategy" value="Submitted" sub="reviewed" color={C.gold} />
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
        {tabs.map((item) => {
          const active = tab === item;
          return (
            <TouchableOpacity key={item} onPress={() => setTab(item)} style={{ paddingHorizontal: 14, paddingVertical: 10, borderRadius: 999, backgroundColor: active ? "rgba(49,230,255,0.14)" : "rgba(255,255,255,0.05)", borderColor: active ? C.cyan : C.border, borderWidth: 1 }}>
              <Text selectable style={{ color: active ? C.cyan : C.text2, fontFamily: font.medium, fontSize: 12, textTransform: "capitalize" }}>
                {item}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {tab === "overview" ? (
        <>
          <GlassCard style={{ padding: 16 }} accent={C.cyan}>
            <SectionTitle
              title="Benchmark vs Portfolio"
              accent={C.cyan}
              right={<Text selectable style={{ color: C.green, fontFamily: font.mono, fontSize: 12 }}>
                Outperforming
              </Text>}
            />
            <LineChart />
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 18 }}>
              <Legend color={C.cyan} label="My Portfolio +8.1%" />
              <Legend color={C.text2} label="Benchmark +5.1%" />
            </View>
          </GlassCard>
          <GlassCard style={{ padding: 16, gap: 12 }} accent={C.purple}>
            <SectionTitle title="Score Components" accent={C.purple} />
            <Progress label="Week 1 Total" value={summary.week1Total} color={C.green} />
            <Progress label="Week 2 Total" value={summary.week2Total} color={C.cyan} />
            <Progress label="Week 3 Total" value={summary.week3Total} color={C.purple} />
            <Progress label="Week 4 Total" value={summary.week4Total} color={C.gold} />
            <Progress label="Final Score" value={Math.round((summary.finalScore / 405) * 100)} color={C.gold} />
          </GlassCard>
        </>
      ) : null}

      {tab === "scoring" ? (
        <GlassCard style={{ padding: 16, gap: 13 }} accent={C.green}>
          <SectionTitle title="Full Scoring Breakdown" accent={C.green} />
          {[
            ["Week 1 Total", summary.week1Total, C.green],
            ["Week 2 Total", summary.week2Total, C.cyan],
            ["Week 3 Total", summary.week3Total, C.purple],
            ["Week 4 Total", summary.week4Total, C.gold],
            ["Final Score Percentage", Math.round((summary.finalScore / 405) * 100), C.red],
          ].map(([label, value, color]) => (
            <Progress key={label as string} label={label as string} value={value as number} color={color as string} />
          ))}
        </GlassCard>
      ) : null}

      {tab === "market" ? (
        <GlassCard style={{ padding: 16, gap: 8 }} accent={C.cyan}>
          {[
            ["NIFTY 50", "24,386", "+0.84%", true],
            ["SENSEX", "80,125", "+0.71%", true],
            ["NIFTY IT", "38,940", "+1.29%", true],
            ["NIFTY PHARMA", "19,420", "-0.22%", false],
          ].map(([name, price, change, up]) => (
            <View key={name as string} style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingVertical: 10, borderBottomColor: C.border, borderBottomWidth: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                {up ? <TrendingUp size={15} color={C.green} /> : <TrendingDown size={15} color={C.red} />}
                <Text selectable style={{ color: C.text1, fontFamily: font.medium, fontSize: 13 }}>
                  {name}
                </Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text selectable style={{ color: C.text0, fontFamily: font.mono, fontSize: 13 }}>
                  {price}
                </Text>
                <Text selectable style={{ color: up ? C.green : C.red, fontFamily: font.mono, fontSize: 11 }}>
                  {change}
                </Text>
              </View>
            </View>
          ))}
        </GlassCard>
      ) : null}

      {tab === "tasks" ? (
        <GlassCard style={{ padding: 16, gap: 12 }} accent={C.gold}>
          <SectionTitle title="This Week's Tasks" accent={C.gold} />
          {[
            ["Register and complete onboarding", true, "Done"],
            ["Submit initial portfolio", true, "Done"],
            ["Write investment thesis", true, "Done"],
            ["Submit Week 3 rebalancing note", false, "Due Jun 8"],
            ["Attend live strategy session", false, "Jun 10, 6PM"],
          ].map(([label, done, due]) => (
            <View key={label as string} style={{ flexDirection: "row", gap: 10, alignItems: "center", borderBottomColor: C.border, borderBottomWidth: 1, paddingBottom: 9 }}>
              <View style={{ width: 18, height: 18, borderRadius: 9, borderWidth: 1, borderColor: done ? C.green : C.border2, backgroundColor: done ? "rgba(30,230,163,0.16)" : "transparent" }} />
              <Text selectable style={{ color: done ? C.text2 : C.text1, flex: 1, fontSize: 13 }}>
                {label}
              </Text>
              <Text selectable style={{ color: done ? C.green : C.text2, fontSize: 11 }}>
                {due}
              </Text>
            </View>
          ))}
        </GlassCard>
      ) : null}
    </View>
  );
}
