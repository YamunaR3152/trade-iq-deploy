import { CheckCircle, CreditCard, Lock, ShieldCheck } from "lucide-react-native";
import { useState } from "react";
import { ScrollView, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { C, font } from "../constants";
import { AppButton, Field, GlassCard, HeaderMini, StepDots } from "../components/ui";

export function PaymentPage({ onComplete }: { onComplete: () => void }) {
  const [processing, setProcessing] = useState(false);
  const [cardNo, setCardNo] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");

  const pay = () => {
    setProcessing(true);
    setTimeout(() => {
      setProcessing(false);
      onComplete();
    }, 900);
  };

  const formatCard = (value: string) => value.replace(/\D/g, "").slice(0, 16).replace(/(.{4})/g, "$1 ").trim();
  const formatExpiry = (value: string) => {
    const digits = value.replace(/\D/g, "").slice(0, 4);
    return digits.length > 2 ? `${digits.slice(0, 2)}/${digits.slice(2)}` : digits;
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg0 }} edges={["top", "left", "right"]}>
      <ScrollView contentInsetAdjustmentBehavior="automatic" style={{ flex: 1 }} contentContainerStyle={{ padding: 20, gap: 18, paddingBottom: 40 }}>
        <HeaderMini title="Course Fees" subtitle="Secure your early access seat" />
        <StepDots current={2} />
        <GlassCard style={{ padding: 18, gap: 16, backgroundColor: "rgba(255,209,102,0.08)", borderColor: "rgba(255,209,102,0.30)" }} accent={C.gold}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: 14 }}>
            <View style={{ flex: 1 }}>
              <Text selectable style={{ color: C.gold, fontFamily: font.medium, fontSize: 12, textTransform: "uppercase" }}>
                Limited-time early access
              </Text>
              <View style={{ flexDirection: "row", alignItems: "flex-end", gap: 10, marginTop: 6 }}>
                <Text selectable style={{ color: C.text2, fontFamily: font.mono, fontSize: 22, textDecorationLine: "line-through" }}>
                  $10
                </Text>
                <Text selectable style={{ color: C.text0, fontFamily: font.mono, fontSize: 42, lineHeight: 48 }}>
                  $7
                </Text>
              </View>
              <Text selectable style={{ color: C.green, fontFamily: font.medium, fontSize: 13, marginTop: 5 }}>
                Save $3 before the deadline
              </Text>
            </View>
            <View style={{ width: 70, height: 70, borderRadius: 26, backgroundColor: "rgba(255,209,102,0.14)", alignItems: "center", justifyContent: "center", borderColor: "rgba(255,209,102,0.40)", borderWidth: 1 }}>
              <ShieldCheck size={36} color={C.gold} />
            </View>
          </View>
          <Text selectable style={{ color: C.text1, fontFamily: font.regular, fontSize: 13, lineHeight: 20 }}>
            Standard registration fee is $10 after the early bird period ends. Register during early access for $7.
          </Text>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
            {["Portfolio tracking", "Mentor sessions", "Certificate"].map((item) => (
              <View key={item} style={{ flexDirection: "row", alignItems: "center", gap: 6, borderRadius: 999, paddingHorizontal: 10, paddingVertical: 7, backgroundColor: "rgba(30,230,163,0.10)", borderColor: "rgba(30,230,163,0.25)", borderWidth: 1 }}>
                <CheckCircle size={13} color={C.green} />
                <Text selectable style={{ color: C.green, fontSize: 11, fontFamily: font.medium }}>
                  {item}
                </Text>
              </View>
            ))}
          </View>
        </GlassCard>

        <GlassCard style={{ padding: 18, gap: 14 }} accent={C.cyan}>
          <Field label="Card number" value={cardNo} onChangeText={(value) => setCardNo(formatCard(value))} placeholder="1234 5678 9012 3456" keyboardType="numeric" />
          <View style={{ flexDirection: "row", gap: 12 }}>
            <View style={{ flex: 1 }}>
              <Field label="Expiry" value={expiry} onChangeText={(value) => setExpiry(formatExpiry(value))} placeholder="MM/YY" keyboardType="numeric" />
            </View>
            <View style={{ flex: 1 }}>
              <Field label="CVV" value={cvv} onChangeText={(value) => setCvv(value.replace(/\D/g, "").slice(0, 3))} placeholder="123" secureTextEntry keyboardType="numeric" />
            </View>
          </View>
          <AppButton label={processing ? "Processing..." : "Pay $7 Early Access Fee"} onPress={pay} icon={<Lock size={16} color={C.green} />} />
          <View style={{ flexDirection: "row", gap: 8, alignItems: "center", justifyContent: "center" }}>
            <CreditCard size={13} color={C.text2} />
            <Text selectable style={{ color: C.text2, fontSize: 11, textAlign: "center" }}>
              Secure educational course registration. No real trading. No real returns.
            </Text>
          </View>
          <AppButton label="Skip for Demo" onPress={onComplete} variant="ghost" />
        </GlassCard>
      </ScrollView>
    </SafeAreaView>
  );
}
