import { ChevronRight } from "lucide-react-native";
import { useEffect, useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { C, font } from "../constants";
import { generateStudentId } from "../auth-store";
import type { UserData } from "../types";
import { formatDobInput, getAge, parseDob } from "../utils";
import { AppButton, Field, GlassCard, HeaderMini, Pill, StepDots } from "../components/ui";

export function RegistrationPage({ onSubmit, onSignIn }: { onSubmit: (data: UserData) => void | Promise<void>; onSignIn: () => void }) {
  const [form, setForm] = useState<UserData>({
    studentId: "",
    fullName: "",
    age: "",
    dateOfBirth: "",
    email: "",
    phoneNumber: "",
    university: "",
    course: "",
    yearOfStudy: "",
    participationType: "Individual",
    teamName: "",
    password: "",
  });
  const [dobError, setDobError] = useState("");

  useEffect(() => {
    let active = true;
    generateStudentId().then((studentId) => {
      if (active) setForm((prev) => ({ ...prev, studentId }));
    });
    return () => {
      active = false;
    };
  }, []);

  const dob = parseDob(form.dateOfBirth);
  const canContinue =
    form.fullName.trim() &&
    dob &&
    Number(form.age) >= 18 &&
    getAge(dob) >= 18 &&
    form.email.includes("@") &&
    form.phoneNumber.trim() &&
    form.university.trim() &&
    form.password.length >= 6 &&
    form.studentId.trim() &&
    (form.participationType === "Individual" || form.teamName.trim());

  const set = (key: keyof UserData) => (value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  const handleContinue = () => {
    const parsedDob = parseDob(form.dateOfBirth);
    if (!parsedDob) {
      setDobError("Use DD/MM/YYYY format.");
      return;
    }
    if (getAge(parsedDob) < 18) {
      setDobError("You must be 18 or older to register.");
      return;
    }
    setDobError("");
    if (canContinue) void onSubmit({ ...form, age: String(getAge(parsedDob)) });
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg0 }} edges={["top", "left", "right"]}>
      <ScrollView contentInsetAdjustmentBehavior="automatic" style={{ flex: 1 }} contentContainerStyle={{ padding: 20, gap: 18, paddingBottom: 40 }}>
        <HeaderMini title="Registration" subtitle="Create your student analyst profile" />
        <StepDots current={0} />
        <GlassCard style={{ padding: 18, gap: 15 }} accent={C.purple}>
          <View style={{ padding: 12, borderRadius: 14, backgroundColor: "rgba(49,230,255,0.10)", borderColor: "rgba(49,230,255,0.25)", borderWidth: 1 }}>
            <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 10, textTransform: "uppercase" }}>
              Auto generated User ID
            </Text>
            <Text selectable style={{ color: C.cyan, fontFamily: font.mono, fontSize: 21, marginTop: 4 }}>
              {form.studentId || "Generating..."}
            </Text>
          </View>
          <Field label="Full Name" value={form.fullName} onChangeText={set("fullName")} placeholder="John Smith" />
          <Field
            label="Date of Birth"
            value={form.dateOfBirth}
            onChangeText={(value) => {
              setDobError("");
              const next = formatDobInput(value);
              const parsed = parseDob(next);
              setForm((prev) => ({ ...prev, dateOfBirth: next, age: parsed ? String(getAge(parsed)) : prev.age }));
            }}
            placeholder="DD/MM/YYYY"
            keyboardType="numeric"
            error={dobError}
          />
          <Field label="Email" value={form.email} onChangeText={(value) => setForm((prev) => ({ ...prev, email: value }))} placeholder="john@university.edu" keyboardType="email-address" />
          <Field label="Phone Number" value={form.phoneNumber} onChangeText={set("phoneNumber")} placeholder="+1234567890" keyboardType="phone-pad" />
          <Field label="University" value={form.university} onChangeText={set("university")} placeholder="NYU" />
          <View style={{ gap: 8 }}>
            <Text selectable style={{ color: C.text2, fontFamily: font.medium, fontSize: 11, textTransform: "uppercase" }}>
              Participation Type
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
              {(["Individual", "Team"] as const).map((option) => (
                <Pill key={option} label={option} active={form.participationType === option} onPress={() => setForm((prev) => ({ ...prev, participationType: option }))} />
              ))}
            </ScrollView>
          </View>
          <Field label="Team Name" value={form.teamName} onChangeText={set("teamName")} placeholder="Alpha Fund (blank if individual)" />
          <Field label="Password" value={form.password} onChangeText={set("password")} placeholder="Minimum 6 characters" secureTextEntry />
          <AppButton label="Continue to Onboarding" onPress={handleContinue} disabled={!canContinue} icon={<ChevronRight size={18} color={C.green} />} />
          <View style={{ flexDirection: "row", justifyContent: "center", gap: 4, flexWrap: "wrap" }}>
            <Text selectable style={{ color: C.text2, fontFamily: font.regular, fontSize: 12 }}>
              Already have an account?
            </Text>
            <TouchableOpacity onPress={onSignIn}>
              <Text selectable style={{ color: C.cyan, fontFamily: font.medium, fontSize: 12 }}>
                Log In
              </Text>
            </TouchableOpacity>
          </View>
        </GlassCard>
      </ScrollView>
    </SafeAreaView>
  );
}