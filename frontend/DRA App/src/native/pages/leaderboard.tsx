import { Text, View } from "react-native";
import { C, font } from "../constants";
import { GlassCard, SectionTitle } from "../components/ui";

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

export function Leaderboard() {
  const rows = [
    ["Priya Mehta", "IIM Ahmedabad", "91.2", "+11.8%", C.gold],
    ["Arjun Sharma", "BITS Pilani", "88.7", "+9.4%", "#cfd6e6"],
    ["Rohan Nair", "NIT Trichy", "85.1", "+8.1%", "#cd7f32"],
    ["Student Analyst", "Your Institution", "78.4", "+6.2%", C.cyan],
    ["Rahul Gupta", "Delhi University", "77.8", "+5.9%", C.text1],
  ] as const;

  return (
    <View style={{ gap: 16 }}>
      <View>
        <Text selectable style={{ color: C.text0, fontFamily: font.medium, fontSize: 25 }}>
          Leaderboard
        </Text>
        <Text selectable style={{ color: C.text2, fontSize: 13, marginTop: 4 }}>
          Weekly ranking blends performance and strategy.
        </Text>
      </View>
      <View style={{ flexDirection: "row", gap: 10 }}>
        <StatCard label="1st Prize" value="$1,000" sub="top score" color={C.gold} />
        <StatCard label="Your Rank" value="#14" sub="overall" color={C.cyan} />
      </View>
      <GlassCard style={{ padding: 12, gap: 8 }} accent={C.gold}>
        <SectionTitle title="Weekly Rankings" accent={C.gold} />
        {rows.map(([name, uni, score, ret, color], index) => (
          <View
            key={name}
            style={{
              padding: 12,
              borderRadius: 14,
              backgroundColor: name === "Student Analyst" ? "rgba(49,230,255,0.10)" : "transparent",
              flexDirection: "row",
              alignItems: "center",
              gap: 12,
            }}
          >
            <Text selectable style={{ width: 30, color, fontFamily: font.mono, fontSize: 16 }}>
              #{index + 1}
            </Text>
            <View style={{ flex: 1 }}>
              <Text selectable style={{ color: name === "Student Analyst" ? C.cyan : C.text0, fontFamily: font.medium, fontSize: 14 }}>
                {name}
              </Text>
              <Text selectable style={{ color: C.text2, fontSize: 11 }}>
                {uni}
              </Text>
            </View>
            <View style={{ alignItems: "flex-end" }}>
              <Text selectable style={{ color: C.text0, fontFamily: font.mono, fontSize: 15 }}>
                {score}
              </Text>
              <Text selectable style={{ color: C.green, fontFamily: font.mono, fontSize: 11 }}>
                {ret}
              </Text>
            </View>
          </View>
        ))}
      </GlassCard>
    </View>
  );
}
