import { useEffect, useState } from "react";
import { useFonts as useLoraFonts, Lora_400Regular, Lora_600SemiBold, Lora_700Bold } from "@expo-google-fonts/lora";
import { useFonts as useNeutonFonts, Neuton_700Bold, Neuton_800ExtraBold } from "@expo-google-fonts/neuton";
import { ActivityIndicator, View } from "react-native";
import type { Flow, UserData } from "./types";
import { clearActiveUser, getActiveUser, saveRegisteredUser, signInUser, signInWithGoogle } from "./auth-store";
import { setUnauthorizedHandler } from "./api";
import Toast, { BaseToast, ErrorToast } from "react-native-toast-message";
import { LandingPage } from "./pages/landing-page";
import { RegistrationPage } from "./pages/registration-page";
import { OnboardingPage } from "./pages/onboarding-page";
import { PaymentPage } from "./pages/payment-page";
import { MainApp } from "./pages/main-app";
import { SignInPage } from "./pages/sign-in-page";

const toastConfig = {
  success: (props: any) => (
    <BaseToast
      {...props}
      style={{
        borderLeftColor: "#32E875",
        backgroundColor: "rgba(255,255,255,0.06)",
        borderRadius: 14,
        borderWidth: 1,
        borderColor: "#32E875",
      }}
      contentContainerStyle={{
        paddingHorizontal: 15,
      }}
      text1Style={{
        color: "#32E875",
        fontSize: 14,
        fontWeight: "700",
      }}
      text2Style={{
        color: "#FFFFFF",
        fontSize: 12,
      }}
    />
  ),
};

export default function ChallengeApp() {
  const [flow, setFlow] = useState<Flow>("landing");
  const [userData, setUserData] = useState<UserData | null>(null);
  const [booting, setBooting] = useState(true);
  const [loraLoaded] = useLoraFonts({ Lora_400Regular, Lora_600SemiBold, Lora_700Bold });
  const [neutonLoaded] = useNeutonFonts({ Neuton_700Bold, Neuton_800ExtraBold });

  useEffect(() => {
    let active = true;
    setUnauthorizedHandler(() => {
      void clearActiveUser();
      setUserData(null);
      setFlow("signin");
    });
    getActiveUser().then((activeUser) => {
      if (!active) return;
      if (activeUser) {
        setUserData(activeUser);
        setFlow("app");
      }
      setBooting(false);
    });
    return () => {
      active = false;
      setUnauthorizedHandler(null);
    };
  }, []);

  if (booting || !loraLoaded || !neutonLoaded) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#060810" }}>
        <ActivityIndicator color="#31E6FF" />
      </View>
    );
  }

  if (flow === "landing") return <LandingPage onExplore={() => setFlow("register")} />;
  if (flow === "signin") {
    return (
      <SignInPage
        onBack={() => setFlow("landing")}
        onSubmit={async (email, password) => {
          try {
            const user = await signInUser(email, password);
            if (!user) return null;
            setUserData(user);
            setFlow("app");
            return user;
          } catch (err) {
            return err instanceof Error ? err.message : "Sign in failed";
          }
        }}
        onGoogleSignIn={async () => {
          try {
            const { user, isNewUser } = await signInWithGoogle();
            setUserData(user);
            setFlow(isNewUser ? "onboarding" : "app");
            return user;
          } catch (err) {
            return err instanceof Error ? err.message : "Google sign in failed";
          }
        }}
      />
    );
  }
  if (flow === "register") {
    return (
      <RegistrationPage
        onSignIn={() => setFlow("signin")}
        onSubmit={async (data) => {
          const savedUser = await saveRegisteredUser(data);
          setUserData(savedUser);
          setFlow("onboarding");
        }}
        onGoogleRegister={async () => {
          try {
            const { user, isNewUser } = await signInWithGoogle();
            setUserData(user);
            setFlow(isNewUser ? "onboarding" : "app");
            return user;
          } catch (err) {
            return err instanceof Error ? err.message : "Google registration failed";
          }
        }}
      />
    );
  }
  if (flow === "onboarding") return <OnboardingPage onComplete={() => setFlow("payment")} />;
  if (flow === "payment") return <PaymentPage onComplete={() => setFlow("app")} />;

return (
  <>
    <MainApp
      userData={userData}
      onLogout={() => {
        void clearActiveUser();
        setUserData(null);
        setFlow("landing");
      }}
    />

   <Toast config={toastConfig} />
  </>
);
}

