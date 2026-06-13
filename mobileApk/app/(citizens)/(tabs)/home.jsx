import React, { useEffect, useRef, useState } from "react";
import {
    View,
    Text,
    TouchableOpacity,
    ScrollView,
    Animated,
    BackHandler,
    Platform,
    KeyboardAvoidingView,
    Modal,
    TextInput,
    Alert,
} from "react-native";
import {
    Feather,
    Ionicons,
    MaterialIcons,
    MaterialCommunityIcons,
} from "@expo/vector-icons";
import { useAuth } from "../../../context/AuthContext";
import { router } from "expo-router";
import ScreenWrapper from "../../../components/ScreenWrapper";
import { useAppContext } from "../../../context/AppContext";
import api from "../../../api/api";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { styled } from "nativewind";
import Toast from "react-native-toast-message";

const StyledAnimatedView = styled(Animated.View);

function EmptyState() {
    return (
        <View className="items-center justify-center py-4 px-8">
            <MaterialCommunityIcons
                name="bell-check-outline"
                size={56}
                color="#d1d5db"
            />
            <Text className="text-gray-700 text-base font-medium mt-4 text-center">
                No active alerts near you
            </Text>
            <Text className="text-gray-300 text-sm mt-1 text-center">
                We'll notify you when something is reported in your area.
            </Text>
        </View>
    );
}

export default function HomeScreen() {
    //for the working modal
    const [modalVisible, setModalVisible] = useState(false);
    const [phone, setPhone] = useState("");
    const [error, setError] = useState("");

    const slideAnim = useRef(new Animated.Value(80)).current;
    const fadeAnim = useRef(new Animated.Value(0)).current;
    const shakeAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        if (!modalVisible) return;
        const subscription = BackHandler.addEventListener(
            "hardwareBackPress",
            () => {
                handleBack();
                return true;
            },
        );
        return () => subscription.remove();
    }, [modalVisible]);

    // Open animation
    useEffect(() => {
        if (modalVisible) {
            slideAnim.setValue(80);
            fadeAnim.setValue(0);
            Animated.parallel([
                Animated.timing(fadeAnim, {
                    toValue: 1,
                    duration: 250,
                    useNativeDriver: true,
                }),
                Animated.spring(slideAnim, {
                    toValue: 0,
                    tension: 65,
                    friction: 10,
                    useNativeDriver: true,
                }),
            ]).start();
        }
    }, [modalVisible]);

    const triggerShake = () => {
        shakeAnim.setValue(0);
        Animated.sequence([
            Animated.timing(shakeAnim, {
                toValue: 10,
                duration: 50,
                useNativeDriver: true,
            }),
            Animated.timing(shakeAnim, {
                toValue: -10,
                duration: 50,
                useNativeDriver: true,
            }),
            Animated.timing(shakeAnim, {
                toValue: 8,
                duration: 50,
                useNativeDriver: true,
            }),
            Animated.timing(shakeAnim, {
                toValue: -8,
                duration: 50,
                useNativeDriver: true,
            }),
            Animated.timing(shakeAnim, {
                toValue: 0,
                duration: 50,
                useNativeDriver: true,
            }),
        ]).start();
    };

    const closeWithAnimation = (cb) => {
        Animated.parallel([
            Animated.timing(fadeAnim, {
                toValue: 0,
                duration: 200,
                useNativeDriver: true,
            }),
            Animated.timing(slideAnim, {
                toValue: 80,
                duration: 200,
                useNativeDriver: true,
            }),
        ]).start(() => {
            setModalVisible(false);
            cb && cb();
        });
    };

    const validatePhone = (number) => {
        const cleaned = number.replace(/[\s\-().]/g, "");
        return /^\+?\d{10,15}$/.test(cleaned);
    };

    const handleSubmit = () => {
        if (!phone.trim()) {
            setError("Please enter your phone number.");
            triggerShake();
            return;
        }
        if (!validatePhone(phone)) {
            setError("Enter a valid phone number (at least 10 digits).");
            triggerShake();
            return;
        }

        Toast.show({
            type: "success",
            text1: `Phone number saved: ${phone.trim()}`,
        });
        setPhone("");
        setError("");
        closeWithAnimation();
        AsyncStorage.setItem("phone", phone.trim());
    };

    const handleBack = () => {
        closeWithAnimation(() => {
            setPhone("");
            setError("");
        });
        logoutCitizen();
        router.replace("/");
    };

    let { logoutCitizen } = useAuth();
    let hour = new Date().getHours();
    const greeting =
        hour < 12
            ? "Good Morning,"
            : hour < 17
              ? "Good Afternoon,"
              : "Good Evening,";

    let { latitude, longitude } = useAppContext();
    let [alerts, setAlerts] = useState([]);
    let getAlerts = async () => {
        let res = await api.post("/geospatial/nearby-sos", {
            longitude: longitude || 0,
            latitude: latitude || 0,
            max_distance_km: 10,
            limit: 20,
        });
        setAlerts(res?.data?.sos_alerts);
    };

    useEffect(() => {
        if (!latitude || !longitude) return;
        getAlerts();
    }, [latitude, longitude]);

    useEffect(() => {
        async function getPhone() {
            let phone = await AsyncStorage.getItem("phone");
            if (!phone) {
                setModalVisible(true);
            }
        }
        getPhone();
        return () => {};
    }, []);

    return (
        <ScreenWrapper>
            <ScrollView
                contentContainerStyle={{ flexGrow: 1 }}
                showsVerticalScrollIndicator={false}
            >
                <View className="flex-1 bg-white">
                    {/* Header */}
                    <View className="px-5 pt-4">
                        <View className="flex-row items-center justify-end">
                            <View className="flex-row items-center gap-4">
                                <TouchableOpacity
                                    onPress={() => {
                                        logoutCitizen();
                                        router.replace("/");
                                    }}
                                >
                                    <Feather
                                        name="log-out"
                                        size={28}
                                        color="black"
                                    />
                                </TouchableOpacity>

                                <TouchableOpacity
                                    onPress={() =>
                                        router.push("/(citizens)/alerts")
                                    }
                                >
                                    <Ionicons
                                        name="notifications-outline"
                                        size={28}
                                        color="#2563eb"
                                    />
                                </TouchableOpacity>
                                <TouchableOpacity>
                                    <Text className="border border-gray-400 px-3 py-2 rounded-lg">
                                        English
                                    </Text>
                                </TouchableOpacity>
                            </View>
                        </View>

                        {/* Greeting */}
                        <View className="mt-7">
                            <Text className="text-black text-[17px] font-semibold">
                                {greeting}
                            </Text>
                            <Text className="text-3xl font-bold text-gray-900">
                                Citizen
                            </Text>
                            <Text className="text-slate-700 mt-1">
                                How can we help you today?
                            </Text>
                        </View>

                        {/* SOS Card */}
                        <TouchableOpacity
                            activeOpacity={0.9}
                            className="bg-red-500 rounded-3xl mt-6 p-10 flex-row items-center shadow-[0_4px_8px_rgba(255,200,20,0.55)]"
                            onPress={() => router.push("/(citizens)/sos")}
                        >
                            <View className="w-26 h-26 rounded-full bg-red-400 items-center justify-center">
                                <MaterialCommunityIcons
                                    name="alarm-light-outline"
                                    size={50}
                                    color="white"
                                />
                            </View>

                            <View className="ml-5 gap-1">
                                <Text className="text-white text-5xl font-bold">
                                    SOS
                                </Text>
                                <Text className="text-white text-xl font-semibold">
                                    Emergency
                                </Text>
                                <Text className="text-red-100 text-base mt-1">
                                    Tap to alert SOS
                                </Text>
                            </View>
                        </TouchableOpacity>

                        {/* Quick Actions */}
                        <View className="mt-8">
                            <Text className="text-xl font-bold text-gray-800 mb-4">
                                Quick Actions
                            </Text>

                            <View className="flex-row justify-between">
                                <QuickAction
                                    icon={
                                        <MaterialIcons
                                            name="report-problem"
                                            size={39}
                                            color="#2563eb"
                                        />
                                    }
                                    label="Report Incident"
                                    link="/(citizens)/report-incident"
                                />

                                <QuickAction
                                    icon={
                                        <Ionicons
                                            name="location"
                                            size={39}
                                            color="#16a34a"
                                        />
                                    }
                                    label="Live Disaster Map"
                                    link="/(citizens)/map"
                                />

                                <QuickAction
                                    icon={
                                        <MaterialCommunityIcons
                                            name="alarm-light-outline"
                                            size={50}
                                            color="red"
                                        />
                                    }
                                    label="Track your SOS"
                                    link="/(citizens)/track-your-SOSs"
                                />

                                <QuickAction
                                    icon={
                                        <Feather
                                            name="phone-call"
                                            size={40}
                                            color="#dc2626"
                                        />
                                    }
                                    label="Emergency Contacts"
                                    link="/(citizens)/helpline"
                                />
                            </View>
                        </View>

                        {/* Alerts */}
                        <View className="mt-8 mb-8">
                            <View className="flex-row items-center justify-between mb-4">
                                <Text className="text-xl font-bold text-gray-800">
                                    Active Alerts Near You
                                </Text>

                                <TouchableOpacity
                                    onPress={() =>
                                        router.push("/(citizens)/alerts")
                                    }
                                >
                                    <Text className="text-blue-600 font-medium">
                                        View All
                                    </Text>
                                </TouchableOpacity>
                            </View>

                            {/* Alert Card 1 */}
                            {alerts.length > 0 ? (
                                <View className="bg-white border border-gray-200 rounded-2xl p-4">
                                    <View className="flex-row items-center justify-between">
                                        <View className="flex-row">
                                            <View className="w-14 h-14 rounded-full bg-red-100 items-center justify-center">
                                                <MaterialCommunityIcons
                                                    name="waves"
                                                    size={26}
                                                    color="#ef4444"
                                                />
                                            </View>

                                            <View className="ml-3">
                                                <Text className="font-semibold text-gray-800 text-xl">
                                                    Flood Alert
                                                </Text>
                                                <Text className="text-gray-500 text-sm">
                                                    Butwal, Rupandehi
                                                </Text>
                                            </View>
                                        </View>

                                        <Text className="text-red-500 text-xs font-medium">
                                            2 min ago
                                        </Text>
                                    </View>

                                    {/* Divider */}
                                    <View className="h-px bg-gray-100 my-4" />

                                    {/* Alert Card 2 */}
                                    <View className="flex-row items-center justify-between">
                                        <View className="flex-row">
                                            <View className="w-14 h-14 rounded-full bg-orange-100 items-center justify-center">
                                                <MaterialIcons
                                                    name="warning-amber"
                                                    size={26}
                                                    color="#f97316"
                                                />
                                            </View>

                                            <View className="ml-3">
                                                <Text className="font-semibold text-gray-800  text-xl">
                                                    Landslide Risk
                                                </Text>
                                                <Text className="text-gray-500 text-sm">
                                                    Palpa, Tanahu
                                                </Text>
                                            </View>
                                        </View>

                                        <Text className="text-orange-500 text-xs font-medium">
                                            16 min ago
                                        </Text>
                                    </View>
                                </View>
                            ) : (
                                <EmptyState />
                            )}
                        </View>
                    </View>
                </View>
                {/* modal view */}
                <Modal
                    visible={modalVisible}
                    transparent
                    animationType="none"
                    statusBarTranslucent
                    onRequestClose={handleBack}
                >
                    <KeyboardAvoidingView
                        className="flex-1 items-center justify-center px-6"
                        behavior={Platform.OS === "ios" ? "padding" : "height"}
                    >
                        {/* Animated backdrop */}
                        <Animated.View
                            style={{ opacity: fadeAnim }}
                            className="absolute inset-0 bg-black/55"
                        />

                        {/* Animated card */}
                        <StyledAnimatedView
                            style={{
                                opacity: Number(fadeAnim),
                                transform: [{ translateY: Number(slideAnim) }],
                            }}
                            className="w-full max-w-sm bg-white rounded-2xl px-6 py-8 shadow-2xl"
                        >
                            <Text className="text-2xl font-bold text-gray-900 mb-1">
                                Enter Your Phone Number
                            </Text>
                            <Text className="text-sm text-gray-500 leading-5 mb-6">
                                Please provide your number to continue, or go
                                back.
                            </Text>

                            {/* Input with shake */}
                            <Animated.View
                                style={{
                                    transform: [{ translateX: shakeAnim }],
                                }}
                                className={`flex-row items-center border-2 rounded-xl px-4 bg-gray-50 mb-1.5 ${
                                    error ? "border-red-500" : "border-gray-200"
                                } ${Platform.OS === "ios" ? "py-3.5" : "py-1"}`}
                            >
                                <Text className="text-lg mr-2.5">📞</Text>
                                <TextInput
                                    className="flex-1 text-base text-gray-900"
                                    placeholder="982 123 4567"
                                    placeholderTextColor="#aaa"
                                    keyboardType="phone-pad"
                                    value={phone}
                                    onChangeText={(text) => {
                                        setPhone(text);
                                        if (error) setError("");
                                    }}
                                    maxLength={20}
                                    returnKeyType="done"
                                    onSubmitEditing={handleSubmit}
                                    autoFocus
                                />
                            </Animated.View>

                            {/* Inline error */}
                            {error ? (
                                <Text className="text-red-500 text-xs mb-3 ml-1">
                                    {error}
                                </Text>
                            ) : null}

                            {/* Submit */}
                            <TouchableOpacity
                                className="bg-blue-600 rounded-xl py-4 items-center mt-4 active:bg-blue-700"
                                onPress={handleSubmit}
                                activeOpacity={0.85}
                            >
                                <Text className="text-white text-base font-bold tracking-wide">
                                    Submit
                                </Text>
                            </TouchableOpacity>

                            {/* Go back */}
                            <TouchableOpacity
                                className="items-center py-4 mt-1"
                                onPress={handleBack}
                                activeOpacity={0.7}
                            >
                                <Text className="text-gray-500 text-sm font-medium">
                                    ← Go Back
                                </Text>
                            </TouchableOpacity>
                        </StyledAnimatedView>
                    </KeyboardAvoidingView>
                </Modal>
            </ScrollView>
        </ScreenWrapper>
    );
}

function QuickAction({ icon, label, link }) {
    return (
        <TouchableOpacity
            className="w-[22%] items-center border border-gray-200 rounded-2xl p-3 gap-2"
            activeOpacity={0.7}
            onPress={() => router.push(link)}
        >
            <View className=" items-center justify-center">{icon}</View>

            <Text
                className="text-center text-gray-700 text-xs mt-2 font-semibold"
                style={{ flexWrap: "wrap", overflow: "hidden" }}
            >
                {label}
            </Text>
        </TouchableOpacity>
    );
}
