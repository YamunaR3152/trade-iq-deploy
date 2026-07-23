import { useEffect, useMemo, useState } from "react";
import { Award, Banknote, Brain, Gauge, PieChart, ShieldCheck, Sparkles, Target } from "lucide-react-native";
import { ActivityIndicator, ScrollView, Text, useWindowDimensions, View } from "react-native";
import { C, font } from "../constants";
import { analytics } from "../api";
import type { BackendScoreBreakdown, BackendScoreCard, BackendScoreInputs, BackendScoreMetrics, BackendWeeklyScore } from "../api";
import { GlassCard, SectionTitle } from "../components/ui";

const scoreMeta: Record<string, { short: string; color: string; Icon: typeof PieChart }> = {
  portfolio_score: { short: "Portfolio", color: C.green, Icon: PieChart },
  risk_score: { short: "Risk", color: C.cyan, Icon: ShieldCheck },
  thesis_score: { short: "Thesis", color: C.purple, Icon: Brain },
  execution_score: { short: "Execution", color: C.gold, Icon: Gauge },
  strategy_score: { short: "Strategy", color: C.red, Icon: Target },
  clean_slate: { short: "Baseline", color: C.text2, Icon: Sparkles },
};

function currency(value: number) {
  return `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function Row({ label, value, color = C.text1 }: { label: string; value: string; color?: string }) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", gap: 12, paddingVertical: 9, borderBottomColor: C.border, borderBottomWidth: 1 }}>
      <Text selectable style={{ color: C.text2, fontSize: 12, flex: 1 }}>{label}</Text>
      <Text selectable style={{ color, fontFamily: font.mono, fontSize: 12, textAlign: "right" }}>{value}</Text>
    </View>
  );
}

function StatPill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={{ flex: 1, minWidth: 150, padding: 12, borderRadius: 8, backgroundColor: `${color}12`, borderColor: `${color}42`, borderWidth: 1 }}>
      <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 10, textTransform: "uppercase" }}>
        {label}
      </Text>
      <Text selectable style={{ color, fontFamily: font.mono, fontSize: 18, marginTop: 6 }}>
        {value}
      </Text>
    </View>
  );
}

function ScoreMetricCard({ label, value, max, color, icon: Icon, compact = false }: { label: string; value: number; max: number; color: string; icon: typeof PieChart; compact?: boolean }) {
  const pct = Math.max(0, Math.min(100, Math.round((value / max) * 100)));
  return (
    <View style={{ flexGrow: 1, flexBasis: compact ? "45%" : 146, minWidth: compact ? 126 : 146, padding: compact ? 11 : 13, borderRadius: 8, backgroundColor: "rgba(5,8,18,0.74)", borderColor: `${color}44`, borderWidth: 1, gap: compact ? 8 : 10 }}>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
        <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 10, textTransform: "uppercase", flex: 1 }}>
          {label}
        </Text>
        <Icon size={16} color={color} />
      </View>
      <Text selectable style={{ color: C.text0, fontFamily: font.mono, fontSize: compact ? 21 : 24 }}>
        {value.toFixed(0)}<Text style={{ color: C.text2, fontSize: 13 }}>/{max}</Text>
      </Text>
      <View style={{ height: 5, borderRadius: 5, backgroundColor: C.bg3, overflow: "hidden" }}>
        <View style={{ width: `${pct}%`, height: "100%", backgroundColor: color }} />
      </View>
    </View>
  );
}

function BreakdownCard({ item, inputs, metrics }: { item: BackendScoreBreakdown; inputs: BackendScoreInputs | null; metrics: BackendScoreMetrics | null }) {
  const meta = scoreMeta[item.key] ?? { short: item.label, color: C.cyan, Icon: Award };
  const Icon = meta.Icon;
  const formula = getBreakdownFormula(item.key, inputs, metrics, item.detail);

  return (
    <View style={{ flex: 1, minWidth: 270, paddingVertical: 8, gap: 6 }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
        <View style={{ width: 18, height: 18, borderRadius: 9, alignItems: "center", justifyContent: "center", borderColor: meta.color, borderWidth: 1 }}>
          <Icon size={11} color={meta.color} />
        </View>
        <View style={{ flex: 1 }}>
          <Text selectable style={{ color: meta.color, fontFamily: font.medium, fontSize: 12, textTransform: "uppercase", letterSpacing: 0 }} numberOfLines={1}>
            {item.label}
          </Text>
        </View>
      </View>
      <Text selectable style={{ color: C.text2, fontSize: 12, lineHeight: 19, paddingLeft: 26 }}>
        {formula.map((part, index) => (
          <Text key={`${item.key}-${index}`} style={{ color: part.highlight ? meta.color : C.text2, fontFamily: part.highlight ? font.medium : font.regular }}>
            {part.text}
          </Text>
        ))}
      </Text>
    </View>
  );
}

function getBreakdownFormula(key: string, inputs: BackendScoreInputs | null, metrics: BackendScoreMetrics | null, fallback: string) {
  const totalCapital = inputs?.total_capital ?? 10000;
  const portfolioValue = metrics?.portfolio_value ?? totalCapital;
  const cashBalance = inputs?.cash_balance ?? metrics?.available_cash_depot ?? 10000;
  const holdingsValue = inputs?.holdings_value ?? metrics?.holdings_value ?? 0;
  const totalTrades = inputs?.total_trades ?? 0;
  const thesisCount = inputs?.trades_with_thesis ?? 0;
  const activeHoldings = inputs?.active_holdings ?? 0;
  const uniqueSectors = inputs?.unique_sectors ?? 0;
  const uniqueTags = inputs?.unique_tags ?? 0;
  const maxAllocation = inputs?.max_allocation ?? 0;
  const returnPct = inputs?.return_on_capital_pct ?? 0;
  const coverage = totalTrades > 0 ? Math.round((thesisCount / totalTrades) * 100) : 0;

  if (key === "portfolio_score") {
    return [
      text("Uses "),
      value(currency(portfolioValue)),
      text(" portfolio value vs "),
      value(currency(totalCapital)),
      text(" starting capital, "),
      value(`${returnPct.toFixed(2)}%`),
      text(" return, and "),
      value(currency(cashBalance)),
      text(" cash remaining."),
    ];
  }

  if (key === "risk_score") {
    return [
      text("Checks "),
      value(String(uniqueSectors)),
      text(" active sectors across "),
      value(String(activeHoldings)),
      text(" positions; max allocation is "),
      value(`${maxAllocation.toFixed(1)}%`),
      text(" on "),
      value(currency(holdingsValue)),
      text(" holdings."),
    ];
  }

  if (key === "thesis_score") {
    return [
      text("Reviews "),
      value(String(thesisCount)),
      text(" submitted theses from "),
      value(String(totalTrades)),
      text(" active trades for clarity, financial logic, market view, and risk awareness."),
    ];
  }

  if (key === "execution_score") {
    return [
      text("Checks "),
      value(String(totalTrades)),
      text(" unique trades, "),
      value(String(uniqueTags)),
      text(" unique tags, and "),
      value(`${thesisCount}/${totalTrades}`),
      text(" thesis coverage ("),
      value(`${coverage}%`),
      text(")."),
    ];
  }

  if (key === "strategy_score") {
    return [
      text("Rewards active portfolio build: "),
      value(String(activeHoldings)),
      text(" active positions, "),
      value(String(uniqueSectors)),
      text(" sectors, and "),
      value(String(totalTrades)),
      text(" submitted trades."),
    ];
  }

  return [text(fallback)];
}

function text(valueText: string) {
  return { text: valueText, highlight: false };
}

function value(valueText: string) {
  return { text: valueText, highlight: true };
}

function WeeklyHistoryTable({ scores }: { scores: BackendWeeklyScore[] }) {
  const columns = [
    { key: "week", label: "Timeline", width: 96 },
    { key: "portfolio", label: "Portfolio", width: 94 },
    { key: "risk", label: "Risk", width: 78 },
    { key: "thesis", label: "Thesis", width: 82 },
    { key: "execution", label: "Execution", width: 92 },
    { key: "strategy", label: "Strategy", width: 86 },
    { key: "total", label: "Total", width: 88 },
    { key: "rank", label: "Rank", width: 72 },
  ];
  const sortedScores = [...scores].sort((a, b) => b.week_number - a.week_number);

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      <View style={{ minWidth: 688 }}>
        <View style={{ flexDirection: "row", paddingBottom: 11, borderBottomColor: C.border2, borderBottomWidth: 1 }}>
          {columns.map((column) => (
            <View key={column.key} style={{ width: column.width, paddingRight: 10 }}>
              <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 10, textTransform: "uppercase" }}>
                {column.label}
              </Text>
            </View>
          ))}
        </View>
        {sortedScores.map((week, index) => (
          <View
            key={week.week_number}
            style={{
              flexDirection: "row",
              alignItems: "center",
              minHeight: 50,
              borderBottomColor: index === sortedScores.length - 1 ? "transparent" : C.border,
              borderBottomWidth: 1,
            }}
          >
            <HistoryCell width={columns[0].width} strong value={`Week ${week.week_number}`} />
            <HistoryCell width={columns[1].width} value={`${week.portfolio_score.toFixed(0)}/40`} />
            <HistoryCell width={columns[2].width} value={`${week.risk_score.toFixed(0)}/20`} />
            <HistoryCell width={columns[3].width} value={`${week.thesis_score.toFixed(0)}/20`} />
            <HistoryCell width={columns[4].width} value={`${week.execution_score.toFixed(0)}/10`} />
            <HistoryCell width={columns[5].width} value={`${week.strategy_score.toFixed(0)}/10`} />
            <HistoryCell width={columns[6].width} value={`${week.final_score.toFixed(0)}/100`} color={week.final_score > 0 ? C.cyan : C.text2} strong />
            <HistoryCell width={columns[7].width} value={week.rank_position ? `#${week.rank_position}` : "Pending"} color={week.rank_position ? C.text1 : C.text2} align="right" strong={Boolean(week.rank_position)} />
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

function HistoryCell({ width, value, color = C.text1, strong, align = "left" }: { width: number; value: string; color?: string; strong?: boolean; align?: "left" | "right" }) {
  return (
    <View style={{ width, paddingRight: 10 }}>
      <Text selectable style={{ color, fontFamily: strong ? font.medium : font.mono, fontSize: 12, textAlign: align }} numberOfLines={1}>
        {value}
      </Text>
    </View>
  );
}

export function Scores({ studentId }: { studentId: string }) {
  const [scores, setScores] = useState<BackendWeeklyScore[]>([]);
  const [currentScore, setCurrentScore] = useState<BackendScoreCard | null>(null);
  const [metrics, setMetrics] = useState<BackendScoreMetrics | null>(null);
  const [inputs, setInputs] = useState<BackendScoreInputs | null>(null);
  const [breakdown, setBreakdown] = useState<BackendScoreBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const { width } = useWindowDimensions();

  useEffect(() => {
    if (!studentId) return;

    setLoading(true);
    setError(false);

    analytics
      .getScores(studentId)
      .then((res) => {
        setScores(res.scores);
        setCurrentScore(res.current_score);
        setMetrics(res.latest_metrics);
        setInputs(res.score_inputs);
        setBreakdown(res.score_breakdown ?? []);
      })
      .catch(() => {
        setError(true);
        setScores([]);
        setCurrentScore(null);
        setMetrics(null);
        setInputs(null);
        setBreakdown([]);
      })
      .finally(() => setLoading(false));
  }, [studentId]);

  const latestWeekScore = scores.length > 0 ? scores.reduce((a, b) => (a.week_number > b.week_number ? a : b)) : null;
  const displayScore = currentScore ?? latestWeekScore;
  const cumulativeScore = scores.reduce((sum, s) => sum + s.final_score, 0);
  const latestRank = latestWeekScore?.rank_position ?? null;
  const cleanSlate = (inputs?.active_holdings ?? 0) === 0;
  const twoColumnScoreLayout = width >= 900;

  const metricCards = useMemo(
    () => [
      { key: "portfolio_score", label: "Portfolio", value: displayScore?.portfolio_score ?? 0, max: 40 },
      { key: "risk_score", label: "Risk", value: displayScore?.risk_score ?? 0, max: 20 },
      { key: "thesis_score", label: "Thesis", value: displayScore?.thesis_score ?? 0, max: 20 },
      { key: "execution_score", label: "Execution", value: displayScore?.execution_score ?? 0, max: 10 },
      { key: "strategy_score", label: "Strategy", value: displayScore?.strategy_score ?? 0, max: 10 },
    ],
    [displayScore],
  );

  return (
    <View style={{ gap: 16 }}>
      <View>
        <Text selectable style={{ color: C.text0, fontFamily: font.heading, fontSize: 29, textTransform: "uppercase" }}>Scores</Text>
        
      </View>

      {loading ? (
        <ActivityIndicator color={C.cyan} />
      ) : error ? (
        <GlassCard style={{ padding: 16 }} accent={C.red}>
          <Text selectable style={{ color: C.red, fontSize: 13 }}>Failed to load scores. Please try again.</Text>
        </GlassCard>
      ) : (
        <>
          <View style={{ flexDirection: twoColumnScoreLayout ? "row" : "column", alignItems: "stretch", gap: 16 }}>
            <GlassCard style={{ flex: twoColumnScoreLayout ? 1 : undefined, minWidth: twoColumnScoreLayout ? 0 : undefined, padding: 16, gap: 14, backgroundColor: "rgba(7,12,27,0.96)", borderColor: "rgba(49,230,255,0.26)" }} accent={C.cyan}>
              <View style={{ flexDirection: "row", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
                <View style={{ flex: 1, minWidth: 230 }}>
                  <SectionTitle title="Total Scorecard" accent={C.cyan}/>
                  <Text selectable style={{ color: C.text2, fontSize: 13, marginTop: 10, lineHeight: 19 }}>
                    {cleanSlate
                      ? "Clean slate active: scores stay at 0 until a portfolio has active holdings."
                      : "Calculated from active holdings, cash balance, sector diversification, thesis coverage, and execution quality."}
                  </Text>
                </View>
                <View style={{ minWidth: 132, paddingHorizontal: 16, paddingVertical: 12, borderRadius: 8, borderWidth: 1, borderColor: "rgba(49,230,255,0.40)", backgroundColor: "rgba(49,230,255,0.10)", alignItems: "center" }}>
                  <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 9, textTransform: "uppercase" }}>
                    Live Total
                  </Text>
                  <Text selectable style={{ color: C.cyan, fontFamily: font.mono, fontSize: 34 }}>
                    {Math.round(displayScore?.final_score ?? 0)}<Text style={{ color: C.text2, fontSize: 13 }}>/100</Text>
                  </Text>
                </View>
              </View>

              <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
                {metricCards.map((card) => {
                  const meta = scoreMeta[card.key];
                  return <ScoreMetricCard key={card.key} label={card.label} value={card.value} max={card.max} color={meta.color} icon={meta.Icon} compact={twoColumnScoreLayout} />;
                })}
              </View>
            </GlassCard>

            <GlassCard style={{ flex: twoColumnScoreLayout ? 1 : undefined, minWidth: twoColumnScoreLayout ? 0 : undefined, padding: 16, gap: 12, backgroundColor: "rgba(7,12,27,0.88)" }} accent={C.purple}>
              <SectionTitle title="Score Breakdown" accent={C.purple} />
              <View style={{ gap: 10 }}>
                {breakdown.map((item) => (
                  <BreakdownCard key={item.key} item={item} inputs={inputs} metrics={metrics} />
                ))}
              </View>
            </GlassCard>
          </View>

          
          {scores.length > 0 ? (
            <GlassCard style={{ padding: 16, gap: 12, backgroundColor: "rgba(7,12,27,0.88)" }} accent={C.green}>
              <SectionTitle title="Weekly History" accent={C.green} />
              <WeeklyHistoryTable scores={scores} />
            </GlassCard>
          ) : null}

          <GlassCard style={{ padding: 16, gap: 10 }} accent={C.gold}>
            <SectionTitle title="Summary" accent={C.gold} right={<Banknote size={16} color={C.gold} />} />
            <Row label="User ID" value={studentId} color={C.cyan} />
            <Row label="Weeks Scored" value={String(scores.length)} />
            <Row label="Cumulative Weekly Score" value={`${cumulativeScore.toFixed(1)} pts`} color={C.green} />
            {latestRank != null ? <Row label="Latest Rank" value={`#${latestRank}`} color={C.cyan} /> : null}
          </GlassCard>
        </>
      )}
    </View>
  );
}
