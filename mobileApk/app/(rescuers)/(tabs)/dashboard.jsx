import React from "react";
import {
    View,
    Text,
    ScrollView,
    Image,
    TouchableOpacity,
    StatusBar,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import ScreenWrapper from "../../../components/ScreenWrapper";

// ── Sample data ────────────────────────────────────────────────────────────────
const USER = {
    name: "Inspector Sharma",
    station: "Butwal Police Office",
    avatar: null, // replace with a URI string to show a real photo
};

const STATS = [
    {
        label: "Assigned\nMissions",
        value: 12,
        color: "text-blue-500",
        border: "border-blue-200",
        bg: "bg-blue-50",
    },
    {
        label: "Pending",
        value: 4,
        color: "text-orange-400",
        border: "border-orange-200",
        bg: "bg-orange-50",
    },
    {
        label: "Completed",
        value: 36,
        color: "text-green-500",
        border: "border-green-200",
        bg: "bg-green-50",
    },
];

const PRIORITY = {
    high: { bg: "bg-red-500", text: "text-white" , cbg: "bg-red-50" , border: "border-red-200"},
    medium: { bg: "bg-orange-400", text: "text-white" , cbg: "bg-orange-50" , border: "border-orange-200"},
    normal: { bg: "bg-blue-500", text: "text-white" , cbg: "bg-blue-50", border: "border-blue-200"},
};

const OPERATIONS = [
    {
        id: 1,
        title: "Flood Rescue",
        location: "Butwal-11, Rupandehi",
        priority: "high",
        icon: "🌊",
        type: "flood",
    },
    {
        id: 2,
        title: "Landslide Report",
        location: "Polpa, Tanahun",
        priority: "medium",
        icon: "⛰️",
        type: "landslide",
    },
    {
        id: 3,
        title: "Accident",
        location: "Siddharth Hwy",
        priority: "normal",
        icon: "🚗",
        type: "accident",
    },
];

const Icons = {
    flood: "🌊",
    landslide: "⛰️",
    accident: "🚗",
    fire: "🔥",
};
// ── Sub-components ─────────────────────────────────────────────────────────────

/** Circular avatar with fallback user-silhouette placeholder */
function Avatar({ uri, size = 52 }) {
    if (uri) {
        return (
            <Image
                source={{ uri }}
                style={{ width: size, height: size, borderRadius: size / 2 }}
                className="bg-gray-200"
            />
        );
    }
    return (
        <View
            style={{ width: size, height: size, borderRadius: size / 2 }}
            className="bg-blue-100 items-center justify-center overflow-hidden"
        >
            {/* Head */}
            <View
                className="bg-blue-400 rounded-full absolute"
                style={{
                    width: size * 0.38,
                    height: size * 0.38,
                    top: size * 0.14,
                }}
            />
            {/* Body / shoulders */}
            <View
                className="bg-blue-400 rounded-t-full absolute bottom-0"
                style={{ width: size * 0.72, height: size * 0.38 }}
            />
        </View>
    );
}

/** Single stat card */
function StatCard({ label, value, color, border, bg }) {
    return (
        <View
            className={`flex-1 mx-1 rounded-2xl border ${border} ${bg} items-center py-4 px-2 pt-6 justify-between`}
        >
            <Text
                className={`text-[15px] font-medium text-center text-gray-500 mb-1 leading-4`}
            >
                {label}
            </Text>
            <Text className={`text-4xl font-bold ${color}`}>{value}</Text>
        </View>
    );
}

/** Single operation row */
function OperationCard({ title, location, priority, type }) {
    const badge = PRIORITY[priority] ?? PRIORITY.Normal;
    let icon = Icons[type];
    // Card background color
    let cbg = PRIORITY[priority].cbg;

    return (
        <View
            className={`flex-row items-center rounded-2xl px-4 py-6 mb-3 shadow-sm ${cbg} border ${PRIORITY[priority].border}`}
            style={{
                elevation: 1,
                shadowColor: "#000",
                shadowOpacity: 0.05,
                shadowRadius: 4,
                shadowOffset: { width: 0, height: 1 },
            }}
        >
            {/* Icon bubble */}
            <View className="w-11 h-11 rounded-full bg-orange-50 items-center justify-center mr-3 overflow-hidden">
                <Text style={{ fontSize: 25 }}>{icon}</Text>
            </View>

            {/* Text */}
            <View className="flex-1">
                <Text className="text-xl font-semibold text-gray-800">
                    {title}
                </Text>
                <Text className="text-[14px] text-gray-400 mt-0.5">
                    {location}
                </Text>
            </View>

            {/* Priority badge */}
            <View className={`${badge.bg} rounded-full px-3 py-1`}>
                <Text
                    className={` ${badge.text} text-xs font-semibold `}
                    style={{ textTransform: "capitalize" }}
                >
                    {priority}
                </Text>
            </View>
        </View>
    );
}

// ── Main screen ────────────────────────────────────────────────────────────────
export default function DashboardScreen() {
    const hour = new Date().getHours();
    const greeting =
        hour < 12
            ? "Good Morning,"
            : hour < 17
              ? "Good Afternoon,"
              : "Good Evening,";

    return (
        <ScreenWrapper>
            <SafeAreaView style={{ flex: 1, backgroundColor: "white" }}>
                <View className="flex-1">
                    <StatusBar
                        barStyle="dark-content"
                        backgroundColor="#F9FAFB"
                    />

                    <ScrollView
                        className="flex-1"
                        contentContainerStyle={{ paddingBottom: 24 }}
                        showsVerticalScrollIndicator={false}
                    >
                        {/* ── Header ── */}
                        <View className="bg-white px-5 pt-12 pb-5">
                            <View className="flex-row items-center">
                                <Avatar uri={USER.avatar} size={65} />
                                <View className="ml-3 flex-1">
                                    <Text className="text-[15px] text-slate-600 font-medium">
                                        {greeting}
                                    </Text>
                                    <Text
                                        className="text-3xl font-bold text-gray-800 mt-0.5"
                                        numberOfLines={1}
                                    >
                                        {USER.name}
                                    </Text>
                                </View>
                            </View>

                            {/* Station */}
                            <View className="mt-6 border border-slate-200 p-7 rounded-2xl shadow-[0_4px_8px_rgba(0,0,0,0.15)]">
                                <Text className="text-[14px] text-gray-400 font-medium uppercase tracking-wide">
                                    Station
                                </Text>
                                <Text className="text-xl font-semibold text-gray-700 mt-0.5">
                                    {USER.station}
                                </Text>
                            </View>
                        </View>

                        {/* ── Stats row ── */}
                        <View className="flex-row px-4 mt-5">
                            {STATS.map((s) => (
                                <StatCard key={s.label} {...s} />
                            ))}
                        </View>

                        {/* ── Today's Operations ── */}
                        <View className="px-4 mt-9">
                            <View className="flex-row items-center justify-between mb-3">
                                <Text className="text-xl font-bold text-gray-800">
                                    Today's Operations
                                </Text>
                                <TouchableOpacity>
                                    <Text className="text-sm text-blue-500 font-medium">
                                        View All
                                    </Text>
                                </TouchableOpacity>
                            </View>

                            {OPERATIONS.map((op) => (
                                <OperationCard key={op.id} {...op} />
                            ))}
                        </View>
                    </ScrollView>
                </View>
            </SafeAreaView>
        </ScreenWrapper>
    );
}
