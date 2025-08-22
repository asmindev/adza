import React from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Link } from "react-router";
import {
    ListPlus,
    ClipboardList,
    BarChart3,
    Users,
    Utensils,
    Star,
    TrendingUp,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import useSWR from "swr";
import { motion } from "framer-motion";
import StatsCard from "@/dashboard/components/StatsCard";
import TopRatedFoodsChart from "@/dashboard/components/charts/TopRatedFoodsChart";

export default function DashboardPage() {
    const {
        data: statsData,
        isLoading,
        error,
    } = useSWR("/api/v1/dashboard/stats");

    // Use error state to conditionally show an error message or fallback data
    const stats = error
        ? {
              totalFoods: 0,
              totalUsers: 0,
              totalReviews: 0,
              averageRating: 0,
              error: true,
          }
        : statsData?.data || {
              totalFoods: 0,
              totalUsers: 0,
              totalReviews: 0,
              averageRating: 0,
          };

    return (
        <div className="space-y-6 w-full">
            <div className="flex flex-col md:flex-row justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-muted-foreground">
                    Selamat datang di dashboard manajemen makanan Anda
                </p>
            </div>

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Ikhtisar</TabsTrigger>
                    <TabsTrigger value="actions">Tindakan Cepat</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    {/* Stats Cards */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <StatsCard
                            title="Total Makanan"
                            value={stats.totalFoods}
                            description="Semua item makanan terdaftar"
                            icon={
                                <Utensils className="h-4 w-4 text-orange-500" />
                            }
                            trend={stats.foodsGrowth || 0}
                        />
                        <StatsCard
                            title="Total Pengguna"
                            value={stats.totalUsers}
                            description="Pengguna terdaftar"
                            icon={<Users className="h-4 w-4 text-blue-500" />}
                            trend={stats.usersGrowth || 0}
                        />
                        <StatsCard
                            title="Total Ulasan"
                            value={stats.totalReviews}
                            description="Ulasan makanan yang dikirimkan"
                            icon={
                                <ClipboardList className="h-4 w-4 text-purple-500" />
                            }
                            trend={stats.reviewsGrowth || 0}
                        />
                        <StatsCard
                            title="Rata-rata Rating"
                            value={stats.averageRating.toFixed(1) || "0.0"}
                            description="Rata-rata rating makanan"
                            icon={<Star className="h-4 w-4 text-yellow-500" />}
                            isRating={true}
                        />
                    </div>

                    {/* Charts Section */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        <Card className="col-span-2">
                            <CardHeader>
                                <CardTitle>Makanan Terpopuler</CardTitle>
                                <CardDescription>
                                    Makanan dengan rating tertinggi di koleksi
                                    Anda
                                </CardDescription>
                            </CardHeader>
                            <CardContent className={"h-full"}>
                                <TopRatedFoodsChart />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Aktivitas Terbaru</CardTitle>
                                <CardDescription>
                                    Aktivitas terbaru di platform
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {isLoading ? (
                                    <div className="flex items-center justify-center h-[200px]">
                                        <p className="text-muted-foreground">
                                            Memuat aktivitas...
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {stats.recentActivities?.length > 0 ? (
                                            stats.recentActivities.map(
                                                (activity, index) => (
                                                    <motion.div
                                                        key={index}
                                                        initial={{
                                                            opacity: 0,
                                                            y: 10,
                                                        }}
                                                        animate={{
                                                            opacity: 1,
                                                            y: 0,
                                                        }}
                                                        transition={{
                                                            delay: index * 0.1,
                                                        }}
                                                        className="flex items-center space-x-2 border-b pb-2"
                                                    >
                                                        <TrendingUp className="h-4 w-4 text-green-500" />
                                                        <div className="space-y-1">
                                                            <p className="text-sm font-medium">
                                                                {activity.title}
                                                            </p>
                                                            <p className="text-xs text-muted-foreground">
                                                                {activity.time}
                                                            </p>
                                                        </div>
                                                    </motion.div>
                                                )
                                            )
                                        ) : (
                                            <p className="text-center text-muted-foreground">
                                                Tidak ada aktivitas terbaru
                                            </p>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="actions" className="space-y-4">
                    <div className="grid gap-6 md:grid-cols-3">
                        <Link to="/dashboard/foods/add" className="block">
                            <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-xl font-bold">
                                        Tambah Makanan
                                    </CardTitle>
                                    <ListPlus className="h-6 w-6 text-orange-500" />
                                </CardHeader>
                                <CardContent>
                                    <CardDescription className="text-md">
                                        Buat item makanan baru dan tambahkan ke
                                        koleksi Anda.
                                    </CardDescription>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link to="/dashboard/foods" className="block">
                            <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-xl font-bold">
                                        Kelola Makanan
                                    </CardTitle>
                                    <ClipboardList className="h-6 w-6 text-blue-500" />
                                </CardHeader>
                                <CardContent>
                                    <CardDescription className="text-md">
                                        Lihat, edit, dan hapus item makanan yang
                                        ada.
                                    </CardDescription>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link to="/dashboard/users" className="block">
                            <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-xl font-bold">
                                        Kelola Pengguna
                                    </CardTitle>
                                    <Users className="h-6 w-6 text-green-500" />
                                </CardHeader>
                                <CardContent>
                                    <CardDescription className="text-md">
                                        Kelola pengguna dan izin mereka.
                                    </CardDescription>
                                </CardContent>
                            </Card>
                        </Link>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
