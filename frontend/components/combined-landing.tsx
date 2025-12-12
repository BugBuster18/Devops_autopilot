"use client";

import React, { useState, useEffect, useRef, Suspense, lazy } from "react";
import { motion, AnimatePresence, LayoutGroup, useScroll, useTransform, useSpring, MotionValue } from "framer-motion";
import { useSession, signIn, signOut } from 'next-auth/react';
import {
    Menu,
    X,
    ArrowRight,
    ChevronRight,
    Mail,
    CheckCircle2,
    Circle,
    CircleAlert,
    CircleDotDashed,
    CircleX,
    Github,
    Zap,
    GitBranch,
    Cloud,
    Code,
    Activity,
    Terminal,
    FileCode,
    Rocket,
    Shield,
    Database,
    Sparkles,
    PlayCircle,
    TrendingUp,
    AlertCircle,
    Clock,
    CheckCircle,
    GitMerge,
    Linkedin,
    Twitter,
    Mic,
    MicOff
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";
import { startDemo, getDemoStatus, DemoStatus } from "../lib/demo-api";
import TogetherAIReportComponent from "./together-ai-report";
import ClineStatusComponent from "./cline-status";
import { MCUTheme, MCUPhases } from "./mcu-theme";

const Spline = lazy(() => import('@splinetool/react-spline'));

// --- Helper Components from Variant 2 ---

const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.6 },
    },
};

const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
        },
    },
};

const itemFadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5 },
    },
};

const fontSize = 40;
const padding = 10;
const height = fontSize + padding;

function Digit({ place, value }: { place: number; value: number }) {
    let valueRoundedToPlace = Math.floor(value / place);
    let animatedValue = useSpring(valueRoundedToPlace);

    useEffect(() => {
        animatedValue.set(valueRoundedToPlace);
    }, [animatedValue, valueRoundedToPlace]);

    return (
        <div style={{ height }} className="relative w-[1ch] tabular-nums">
            {[...Array(10)].map((_, i) => (
                <Number key={i} mv={animatedValue} number={i} />
            ))}
        </div>
    );
}

function Number({ mv, number }: { mv: MotionValue; number: number }) {
    let y = useTransform(mv, (latest: number) => {
        let placeValue = latest % 10;
        let offset = (10 + number - placeValue) % 10;

        let memo = offset * height;

        if (offset > 5) {
            memo -= 10 * height;
        }

        return memo;
    });

    return (
        <motion.span
            style={{ y }}
            className="absolute inset-0 flex items-center justify-center"
        >
            {number}
        </motion.span>
    );
}

function Counter({ start = 0, end, duration = 2, className, fontSize = 30 }: { start?: number, end: number, duration?: number, className?: string, fontSize?: number }) {
    const [value, setValue] = useState(start);

    useEffect(() => {
        const interval = setInterval(() => {
            if (value < end) {
                setValue((prev) => prev + 1);
            }
        }, (duration / (end - start)) * 1000);

        return () => clearInterval(interval);
    }, [value, end, start, duration]);

    return (
        <div
            style={{ fontSize }}
            className={cn(
                "flex overflow-hidden rounded px-2 leading-none text-primary font-bold",
                className
            )}
        >
            {value >= 100000 && <Digit place={100000} value={value} />}
            {value >= 10000 && <Digit place={10000} value={value} />}
            {value >= 1000 && <Digit place={1000} value={value} />}
            {value >= 100 && <Digit place={100} value={value} />}
            {value >= 10 && <Digit place={10} value={value} />}
            <Digit place={1} value={value} />
        </div>
    );
}

function HeroSplineBackground() {
    return (
        <div style={{
            position: 'relative',
            width: '100%',
            height: '100vh',
            pointerEvents: 'auto',
            overflow: 'hidden',
        }}>
            {/* MCU-inspired animated background */}
            <div className="absolute inset-0 bg-gradient-to-br from-black via-blue-900/30 via-red-900/20 to-black">
                {/* Animated particles effect */}
                <div className="absolute inset-0 overflow-hidden">
                    {[...Array(20)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute w-1 h-1 bg-white rounded-full"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                            }}
                            animate={{
                                y: [0, -100, 0],
                                opacity: [0, 1, 0],
                                scale: [0, 1, 0],
                            }}
                            transition={{
                                duration: 3 + Math.random() * 2,
                                repeat: Infinity,
                                delay: Math.random() * 2,
                            }}
                        />
                    ))}
                </div>
                
                {/* MCU-style energy waves */}
                <motion.div
                    className="absolute inset-0 opacity-20"
                    style={{
                        background: `radial-gradient(circle at 50% 50%, 
                            ${MCUTheme.colors.ironMan.glow} 0%, 
                            ${MCUTheme.colors.captainAmerica.glow} 30%, 
                            transparent 70%)`,
                    }}
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.1, 0.3, 0.1],
                    }}
                    transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            </div>
            
            <Suspense fallback={<div className="w-full h-full bg-gradient-to-br from-black via-blue-900/30 to-black" />}>
                <Spline
                    style={{
                        width: '100%',
                        height: '100vh',
                        pointerEvents: 'auto',
                    }}
                    scene="https://prod.spline.design/us3ALejTXl6usHZ7/scene.splinecode"
                />
            </Suspense>
            <div
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100vh',
                    background: `
            linear-gradient(to right, rgba(0, 0, 0, 0.85), transparent 30%, transparent 70%, rgba(0, 0, 0, 0.85)),
            linear-gradient(to bottom, transparent 40%, rgba(0, 0, 0, 0.95))
          `,
                    pointerEvents: 'none',
                }}
            />
        </div>
    );
}

function Navbar() {
    const [hoveredNavItem, setHoveredNavItem] = useState<string | null>(null);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { data: session, status } = useSession();

    const handleMouseEnterNavItem = (item: string) => setHoveredNavItem(item);
    const handleMouseLeaveNavItem = () => setHoveredNavItem(null);

    const toggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen);
    };

    const navLinkClass = (itemName: string, extraClasses = '') => {
        const isCurrentItemHovered = hoveredNavItem === itemName;
        const isAnotherItemHovered = hoveredNavItem !== null && !isCurrentItemHovered;

        const colorClass = isCurrentItemHovered
            ? 'text-white'
            : isAnotherItemHovered
                ? 'text-gray-500'
                : 'text-gray-300';

        return `text-sm transition duration-150 ${colorClass} ${extraClasses}`;
    };

    const handleGitHubLogin = () => {
        signIn('github');
    };

    const handleLogout = () => {
        signOut();
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50" style={{ backgroundColor: 'rgba(13, 13, 24, 0.3)', backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)', borderRadius: '0 0 15px 15px' }}>
            <div className="container mx-auto px-4 py-4 md:px-6 lg:px-8 flex items-center justify-between">
                <div className="flex items-center space-x-6 lg:space-x-8">
                    <div className="text-white flex items-center space-x-3">
                        <motion.div
                            whileHover={{ rotate: 5, scale: 1.1 }}
                            transition={{ type: "spring", stiffness: 400, damping: 10 }}
                            className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 via-blue-500 to-teal-500 flex items-center justify-center"
                        >
                            <Rocket className="h-5 w-5 text-white" />
                        </motion.div>
                        <span className="font-bold text-xl">DevOps Autopilot</span>
                    </div>

                    <div className="hidden lg:flex items-center space-x-6">
                        <div className="relative group" onMouseEnter={() => handleMouseEnterNavItem('features')} onMouseLeave={handleMouseLeaveNavItem}>
                            <a href="#features" className={navLinkClass('features', 'flex items-center')}>
                                Features
                                <ChevronRight className="ml-1 w-3 h-3 group-hover:rotate-90 transition-transform duration-200" />
                            </a>
                        </div>

                        <div className="relative group" onMouseEnter={() => handleMouseEnterNavItem('agents')} onMouseLeave={handleMouseLeaveNavItem}>
                            <a href="#agents" className={navLinkClass('agents', 'flex items-center')}>
                                Agents
                                <ChevronRight className="ml-1 w-3 h-3 group-hover:rotate-90 transition-transform duration-200" />
                            </a>
                        </div>

                        <div className="relative group" onMouseEnter={() => handleMouseEnterNavItem('workflow')} onMouseLeave={handleMouseLeaveNavItem}>
                            <a href="#workflow" className={navLinkClass('workflow', 'flex items-center')}>
                                Workflow
                                <ChevronRight className="ml-1 w-3 h-3 group-hover:rotate-90 transition-transform duration-200" />
                            </a>
                        </div>

                        <a href="#contact" className={navLinkClass('contact')} onMouseEnter={() => handleMouseEnterNavItem('contact')} onMouseLeave={handleMouseLeaveNavItem}>
                            Contact
                        </a>
                    </div>
                </div>

                <div className="flex items-center space-x-4 md:space-x-6">
                    <a href="#" className="hidden sm:block text-gray-300 hover:text-white text-sm">Documentation</a>
                    {status === 'loading' ? (
                        <div className="text-gray-300">Loading...</div>
                    ) : session ? (
                        <div className="flex items-center space-x-4">
                            <span className="text-gray-300 text-sm">Welcome, {session.user?.name}</span>
                            <Button onClick={handleLogout} variant="outline" size="sm" className="rounded-full bg-white/10 backdrop-blur-sm border-white/30 text-white hover:bg-white/20">
                                Logout
                            </Button>
                        </div>
                    ) : (
                        <Button onClick={handleGitHubLogin} variant="outline" size="sm" className="rounded-full bg-white/10 backdrop-blur-sm border-white/30 text-white hover:bg-white/20">
                            <Github className="mr-2 h-4 w-4" />
                            Login with GitHub
                        </Button>
                    )}
                    <a href="#" className="bg-[#8200DB29] hover:bg-black/50 text-white font-semibold py-2 px-5 rounded-full text-sm md:text-base border border-[#322D36]" style={{ backdropFilter: 'blur(8px)' }}>Get Started</a>
                    <button className="lg:hidden text-white p-2" onClick={toggleMobileMenu} aria-label="Toggle mobile menu">
                        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>
            </div>

            <div className={`lg:hidden bg-black bg-opacity-50 border-t border-gray-700/30 absolute top-full left-0 right-0 z-30
           overflow-hidden transition-all duration-300 ease-in-out
           ${isMobileMenuOpen ? 'max-h-screen opacity-100 pointer-events-auto' : 'max-h-0 opacity-0 pointer-events-none'}
           `}
                style={{ backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)' }}
            >
                <div className="px-4 py-6 flex flex-col space-y-4">
                    {['Features', 'Agents', 'Workflow', 'Contact'].map((item, index) => (
                        <motion.div key={index} variants={itemFadeIn}>
                            <a
                                href={`#${item.toLowerCase()}`}
                                className="flex items-center justify-between rounded-3xl px-3 py-2 text-lg font-medium text-gray-300 hover:text-gray-100 hover:bg-white/10"
                                onClick={toggleMobileMenu}
                            >
                                {item}
                                <ChevronRight className="h-4 w-4" />
                            </a>
                        </motion.div>
                    ))}
                </div>
            </div>
        </nav>
    );
}

// --- Combined Hero Content (Variant 2 Layout + Variant 3 Elements) ---

function HeroContent({ onStartDemo, isDemoActive }: { onStartDemo: (url: string) => void, isDemoActive: boolean }) {
    const [stats, setStats] = useState({
        bugs: 0,
        deployments: 0,
        uptime: 0
    });
    const [repoUrl, setRepoUrl] = useState("");

    useEffect(() => {
        const animateStats = () => {
            const duration = 2000;
            const steps = 60;
            const interval = duration / steps;
            let step = 0;

            const timer = setInterval(() => {
                step++;
                const progress = step / steps;
                setStats({
                    bugs: Math.floor(progress * 247),
                    deployments: Math.floor(progress * 1543),
                    uptime: Math.floor(progress * 99.9 * 10) / 10
                });

                if (step >= steps) clearInterval(timer);
            }, interval);

            return () => clearInterval(timer);
        };

        const timeout = setTimeout(animateStats, 500);
        return () => clearTimeout(timeout);
    }, []);

    const handleStartClick = (e: React.FormEvent) => {
        e.preventDefault();
        if (repoUrl) {
            onStartDemo(repoUrl);
        }
    };

    return (
        <div className="text-left text-white pt-16 sm:pt-24 md:pt-32 px-4 max-w-4xl">
            <motion.div
                initial={{ opacity: 0, scale: 0.8, x: -20 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                transition={{ duration: 0.6, type: "spring", stiffness: 200 }}
                className="inline-flex items-center rounded-full bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-blue-500/20 px-4 py-2 text-sm mb-6 backdrop-blur-sm border border-yellow-500/30 shadow-lg shadow-yellow-500/20"
            >
                <motion.span
                    className="w-2 h-2 bg-gradient-to-r from-red-500 to-yellow-500 rounded-full mr-2"
                    animate={{
                        scale: [1, 1.3, 1],
                        boxShadow: [
                            "0 0 0 0 rgba(255, 215, 0, 0.7)",
                            "0 0 0 10px rgba(255, 215, 0, 0)",
                            "0 0 0 0 rgba(255, 215, 0, 0)",
                        ],
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                    }}
                />
                <span className="bg-gradient-to-r from-red-400 via-yellow-400 to-blue-400 bg-clip-text text-transparent font-semibold">
                    🛡️ Avengers Initiative - Multi-Agent DevOps
                </span>
            </motion.div>
            <motion.h1
                {...MCUTheme.animations.cinematic.heroEntrance}
                transition={{ duration: 1.2, delay: 0.2 }}
                className="text-4xl sm:text-5xl md:text-7xl font-bold mb-6 leading-tight tracking-wide relative"
            >
                <motion.span
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="block"
                >
                    Autonomous{" "}
                    <span className="bg-gradient-to-r from-red-500 via-yellow-500 to-blue-500 bg-clip-text text-transparent animate-pulse">
                        DevOps
                    </span>
                </motion.span>
                <motion.span
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="block mt-2"
                >
                    From Bug to Deploy
                </motion.span>
                {/* MCU-style glow effect */}
                <motion.div
                    className="absolute -inset-4 bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-blue-500/20 blur-3xl -z-10"
                    animate={{
                        opacity: [0.3, 0.6, 0.3],
                        scale: [1, 1.1, 1],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            </motion.h1>
            <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.4 }}
                className="text-base sm:text-lg md:text-xl mb-8 opacity-80 max-w-2xl"
            >
                Clone → Analyze → Fix → Test → Deploy → Review → Report.
                All automated with multiple AI agents working in perfect harmony.
            </motion.p>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.6 }}
                className="pointer-events-auto mb-8"
            >
                <form onSubmit={handleStartClick} className="flex flex-col sm:flex-row gap-3 max-w-lg">
                    <Input
                        placeholder="Enter GitHub Repo URL (e.g., https://github.com/user/repo)"
                        className="rounded-full bg-white/10 border-white/20 text-white placeholder:text-gray-400 flex-1"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                    />
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button 
                            type="submit" 
                            size="lg" 
                            disabled={isDemoActive} 
                            className="relative rounded-full bg-gradient-to-r from-red-600 via-yellow-500 to-blue-600 hover:from-red-700 hover:via-yellow-600 hover:to-blue-700 text-white font-bold group whitespace-nowrap overflow-hidden shadow-2xl shadow-yellow-500/30"
                        >
                            {/* MCU-style shimmer effect */}
                            <motion.div
                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                                animate={{
                                    x: ["-100%", "100%"],
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity,
                                    repeatDelay: 1,
                                }}
                            />
                            <span className="relative z-10 flex items-center">
                                {isDemoActive ? "⚡ Avengers Assemble..." : "🚀 Assemble the Team"}
                                {!isDemoActive && (
                                    <motion.div
                                        animate={{ rotate: [0, 360] }}
                                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                    >
                                        <Rocket className="ml-2 h-5 w-5" />
                                    </motion.div>
                                )}
                                {isDemoActive && <CircleDotDashed className="ml-2 h-5 w-5 animate-spin" />}
                            </span>
                        </Button>
                    </motion.div>
                </form>
            </motion.div>

            {/* Stats from Variant 3 */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1, delay: 0.8 }}
                className="flex items-center space-x-8 pt-4 text-sm text-gray-400"
            >
                <div className="text-center">
                    <motion.div
                        className="font-semibold text-white text-2xl"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {stats.bugs}+
                    </motion.div>
                    <div>Bugs Fixed</div>
                </div>
                <div className="w-px h-8 bg-white/20"></div>
                <div className="text-center">
                    <motion.div
                        className="font-semibold text-white text-2xl"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {stats.deployments}+
                    </motion.div>
                    <div>Deployments</div>
                </div>
                <div className="w-px h-8 bg-white/20"></div>
                <div className="text-center">
                    <motion.div
                        className="font-semibold text-white text-2xl"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {stats.uptime}%
                    </motion.div>
                    <div>Uptime</div>
                </div>
            </motion.div>
        </div>
    );
}

// --- Agent Workflow Dashboard (Variant 3) ---

interface WorkflowStep {
    id: string;
    name: string;
    service: string;
    purpose: string;
    status: "completed" | "in-progress" | "pending" | "need-help" | "failed";
    agent: string;
    icon: React.ReactNode;
}

function AgentWorkflowDashboard({ workflowStatus, executionId, repoUrl }: { 
    workflowStatus: DemoStatus | null;
    executionId?: string;
    repoUrl?: string;
}) {
    const [steps, setSteps] = useState<WorkflowStep[]>([
        {
            id: "1",
            name: "Clone Repository",
            service: "git.clone",
            purpose: "Download source code from GitHub",
            status: "pending",
            agent: "Nick Fury (Git)",
            icon: <Github className="h-5 w-5" />
        },
        {
            id: "2",
            name: "AI Bug Analysis",
            service: "ai.generate",
            purpose: "Scan codebase using Oumi",
            status: "pending",
            agent: "Vision (Oumi)",
            icon: <Zap className="h-5 w-5" />
        },
        {
            id: "3",
            name: "Auto-Fix Code",
            service: "agent.execute",
            purpose: "Cline applies fixes",
            status: "pending",
            agent: "Iron Man (Cline)",
            icon: <Code className="h-5 w-5" />
        },
        {
            id: "4",
            name: "Run CI/CD",
            service: "kestra.workflow",
            purpose: "Run tests and build",
            status: "pending",
            agent: "Captain America (Kestra)",
            icon: <Activity className="h-5 w-5" />
        },
        {
            id: "5",
            name: "Deploy to Vercel",
            service: "vercel.deploy",
            purpose: "Deploy production build",
            status: "pending",
            agent: "Thor (Vercel)",
            icon: <Cloud className="h-5 w-5" />
        },
        {
            id: "6",
            name: "Code Review",
            service: "agent.execute",
            purpose: "CodeRabbit reviews code",
            status: "pending",
            agent: "Black Widow (CodeRabbit)",
            icon: <FileCode className="h-5 w-5" />
        },
        {
            id: "7",
            name: "Generate Report",
            service: "ai.generate",
            purpose: "Together AI summarizes",
            status: "pending",
            agent: "Doctor Strange (Together AI)",
            icon: <Terminal className="h-5 w-5" />
        }
    ]);

    useEffect(() => {
        if (workflowStatus) {
            setSteps(prevSteps => prevSteps.map(step => {
                const backendStep = workflowStatus.steps.find(s => s.id === step.id);
                if (backendStep) {
                    return { ...step, status: backendStep.status as any };
                }
                return step;
            }));
        }
    }, [workflowStatus]);

    const prefersReducedMotion =
        typeof window !== 'undefined'
            ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
            : false;

    const taskVariants = {
        hidden: {
            opacity: 0,
            y: prefersReducedMotion ? 0 : -5
        },
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                type: prefersReducedMotion ? "tween" : "spring",
                stiffness: 500,
                damping: 30,
                duration: prefersReducedMotion ? 0.2 : undefined
            }
        }
    };

    return (
        <section id="workflow" className="py-20 px-4 relative overflow-hidden bg-black">
            <div className="max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="inline-block rounded-full bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-blue-500/20 px-4 py-2 text-sm mb-4 backdrop-blur-sm border border-yellow-500/30 shadow-lg"
                    >
                        <Activity className="inline mr-2 h-4 w-4 text-yellow-400 animate-pulse" />
                        <span className="bg-gradient-to-r from-red-400 via-yellow-400 to-blue-400 bg-clip-text text-transparent font-semibold">
                            Mission Control - Live Dashboard
                        </span>
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-red-400 via-yellow-400 to-blue-400 bg-clip-text text-transparent"
                    >
                        The Avengers Initiative
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="text-gray-300 text-lg max-w-2xl mx-auto"
                    >
                        Watch Earth's mightiest heroes collaborate in perfect harmony to analyze, fix, test, and deploy your code automatically
                    </motion.p>
                </motion.div>

                <div className="bg-white/5 border border-white/10 rounded-xl shadow-2xl overflow-hidden backdrop-blur-sm">
                    <LayoutGroup>
                        <div className="p-4 overflow-hidden">
                            <ul className="space-y-1 overflow-hidden">
                                {steps.map((step, index) => {
                                    const isCompleted = step.status === "completed";

                                    return (
                                        <motion.li
                                            key={step.id}
                                            className={`${index !== 0 ? "mt-1 pt-2" : ""}`}
                                            initial="hidden"
                                            whileInView="visible"
                                            viewport={{ once: true }}
                                            variants={taskVariants}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <motion.div
                                                className="group flex items-center px-3 py-3 rounded-md hover:bg-gradient-to-r hover:from-red-500/10 hover:via-yellow-500/10 hover:to-blue-500/10 transition-all duration-300 border-l-2 border-transparent hover:border-yellow-500/50"
                                                whileHover={{ x: 5 }}
                                            >
                                                <motion.div
                                                    className="mr-3 flex-shrink-0"
                                                    whileHover={{ scale: 1.1 }}
                                                >
                                                    <AnimatePresence mode="wait">
                                                        <motion.div
                                                            key={step.status}
                                                            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                                                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                                            exit={{ opacity: 0, scale: 0.8, rotate: 10 }}
                                                            transition={{
                                                                duration: 0.2,
                                                                ease: [0.2, 0.65, 0.3, 0.9]
                                                            }}
                                                        >
                                                            {step.status === "completed" ? (
                                                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                                                            ) : step.status === "in-progress" ? (
                                                                <CircleDotDashed className="h-5 w-5 text-blue-500 animate-spin" />
                                                            ) : step.status === "need-help" ? (
                                                                <CircleAlert className="h-5 w-5 text-yellow-500" />
                                                            ) : step.status === "failed" ? (
                                                                <CircleX className="h-5 w-5 text-red-500" />
                                                            ) : (
                                                                <Circle className="text-gray-600 h-5 w-5" />
                                                            )}
                                                        </motion.div>
                                                    </AnimatePresence>
                                                </motion.div>

                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-3 mb-1">
                                                        <span className={`font-medium text-gray-200 ${isCompleted ? "text-gray-500 line-through" : ""}`}>
                                                            {step.name}
                                                        </span>
                                                        <span className="text-xs text-gray-500 border border-gray-700 rounded px-1.5 py-0.5">
                                                            {step.agent}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-400">
                                                        {step.purpose}
                                                    </p>
                                                </div>

                                                <div className="flex items-center gap-2 ml-4">
                                                    <div className="p-2 rounded-md bg-white/5 text-gray-300">
                                                        {step.icon}
                                                    </div>
                                                    <motion.span
                                                        className={`rounded px-2 py-1 text-xs font-medium ${step.status === "completed"
                                                            ? "bg-green-500/20 text-green-400"
                                                            : step.status === "in-progress"
                                                                ? "bg-blue-500/20 text-blue-400"
                                                                : step.status === "need-help"
                                                                    ? "bg-yellow-500/20 text-yellow-400"
                                                                    : step.status === "failed"
                                                                        ? "bg-red-500/20 text-red-400"
                                                                        : "bg-gray-800 text-gray-500"
                                                            }`}
                                                        initial={{ scale: 1 }}
                                                        animate={{
                                                            scale: [1, 1.08, 1],
                                                            transition: {
                                                                duration: 0.35,
                                                                ease: [0.34, 1.56, 0.64, 1]
                                                            }
                                                        }}
                                                        key={step.status}
                                                    >
                                                        {step.status}
                                                    </motion.span>
                                                </div>
                                            </motion.div>
                                        </motion.li>
                                    );
                                })}
                            </ul>
                        </div>
                    </LayoutGroup>
                    
                    {/* Together AI and Cline Components */}
                    {executionId && (
                        <div className="p-4 space-y-4 border-t border-white/10">
                            {(steps.find(s => s.id === "3")?.status === "in-progress" || steps.find(s => s.id === "3")?.status === "completed") && (
                                <ClineStatusComponent executionId={executionId} repoUrl={repoUrl} />
                            )}
                            {(steps.find(s => s.id === "7")?.status === "in-progress" || steps.find(s => s.id === "7")?.status === "completed") && (
                                <TogetherAIReportComponent executionId={executionId} repoUrl={repoUrl} />
                            )}
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}

// --- Features Section (Variant 2) ---

function FeaturesSection() {
    return (
        <section id="features" className="relative py-16 md:py-24 bg-black">
            <div className="container mx-auto px-4 md:px-6 lg:px-8">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeIn}
                    className="text-center mb-12"
                >
                    <div className="inline-block rounded-full bg-blue-500/20 px-4 py-2 text-sm mb-4 backdrop-blur-sm border border-blue-500/30">
                        <Zap className="inline mr-2 h-4 w-4 text-blue-400" />
                        Key Features
                    </div>
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                        Everything You Need for <span className="bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">Autonomous DevOps</span>
                    </h2>
                </motion.div>

                <div className="grid gap-4 sm:grid-cols-5">
                    <Card className="group overflow-hidden shadow-black/5 sm:col-span-3 sm:rounded-3xl bg-gradient-to-br from-purple-900/20 to-black border-purple-500/30">
                        <CardHeader>
                            <div className="md:p-6">
                                <p className="font-medium text-white text-xl">AI-Powered Bug Detection</p>
                                <p className="text-gray-400 mt-3 max-w-sm text-sm">Advanced machine learning algorithms scan your entire codebase for bugs, security vulnerabilities, and performance issues in seconds.</p>
                            </div>
                        </CardHeader>
                        <div className="relative h-fit pl-6 md:pl-12">
                            <div className="absolute -inset-6 bg-gradient-to-b from-transparent to-black"></div>
                            <div className="bg-black/80 overflow-hidden rounded-tl-3xl border-l border-t border-purple-500/30 pl-2 pt-2">
                                <div className="bg-gradient-to-br from-purple-900/40 to-black p-8 rounded-tl-2xl">
                                    <div className="space-y-2">
                                        <div className="flex items-center space-x-2">
                                            <AlertCircle className="h-4 w-4 text-red-400" />
                                            <span className="text-sm text-gray-300">3 Critical Issues Found</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <Clock className="h-4 w-4 text-yellow-400" />
                                            <span className="text-sm text-gray-300">12 Performance Warnings</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <CheckCircle className="h-4 w-4 text-green-400" />
                                            <span className="text-sm text-gray-300">Auto-fix Available</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Card>

                    <Card className="group overflow-hidden shadow-black/5 sm:col-span-2 sm:rounded-3xl bg-gradient-to-br from-blue-900/20 to-black border-blue-500/30">
                        <CardHeader className="text-center">
                            <p className="mx-auto my-6 max-w-md text-balance text-lg font-semibold text-white sm:text-2xl md:p-6">
                                Deploy in Minutes, Not Hours
                            </p>
                        </CardHeader>
                        <CardContent className="mt-auto h-fit">
                            <div className="relative mb-6 sm:mb-0">
                                <div className="flex justify-center items-center space-x-4 p-6">
                                    <div className="text-center">
                                        <Counter end={3} duration={2} fontSize={48} className="text-blue-400" />
                                        <p className="text-xs text-gray-400 mt-2">Minutes</p>
                                    </div>
                                    <ArrowRight className="h-8 w-8 text-blue-400" />
                                    <div className="text-center">
                                        <CheckCircle className="h-12 w-12 text-green-400 mx-auto" />
                                        <p className="text-xs text-gray-400 mt-2">Deployed</p>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="group p-6 shadow-black/5 sm:col-span-2 sm:rounded-3xl md:p-12 bg-gradient-to-br from-teal-900/20 to-black border-teal-500/30">
                        <p className="mx-auto mb-12 max-w-md text-balance text-center text-lg font-semibold text-white sm:text-2xl">
                            Real-time Monitoring & Alerts
                        </p>
                        <div className="flex justify-center gap-6">
                            <div className="relative flex aspect-square size-16 items-center rounded-2xl border border-teal-500/30 p-3 shadow-lg bg-teal-500/10">
                                <Activity className="mt-auto size-8 text-teal-400" />
                            </div>
                            <div className="relative flex aspect-square size-16 items-center rounded-2xl border border-teal-500/30 p-3 shadow-lg bg-teal-500/10">
                                <TrendingUp className="mt-auto size-8 text-teal-400" />
                            </div>
                        </div>
                    </Card>

                    <Card className="group relative shadow-black/5 sm:col-span-3 sm:rounded-3xl bg-gradient-to-br from-orange-900/20 to-black border-orange-500/30">
                        <CardHeader className="p-6 md:p-12">
                            <p className="font-medium text-white text-xl">Multi-Platform Integration</p>
                            <p className="text-gray-400 mt-2 max-w-sm text-sm">Seamlessly connects with GitHub, Vercel, and all major DevOps tools</p>
                        </CardHeader>
                        <CardContent className="relative h-fit px-6 pb-6 md:px-12 md:pb-12">
                            <div className="grid grid-cols-4 gap-2 md:grid-cols-6">
                                {[Github, Database, Terminal, Code, GitBranch, Rocket].map((Icon, i) => (
                                    <div key={i} className="rounded-2xl bg-orange-500/10 flex aspect-square items-center justify-center border border-orange-500/30 p-4 hover:bg-orange-500/20 transition-colors">
                                        <Icon className="size-8 text-orange-400" />
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </section>
    );
}

// --- Agents Section (Variant 2) ---

function AgentsSection() {
    const agents = [
        {
            name: "Iron Man (Cline)",
            role: "Code Architect",
            description: "Genius, billionaire, playboy, philanthropist... and automated code fixer.",
            icon: Code,
            color: "from-red-500 to-yellow-500"
        },
        {
            name: "Captain America (Kestra)",
            role: "Workflow Commander",
            description: "Orchestrates the entire mission with tactical precision and leadership.",
            icon: GitMerge,
            color: "from-blue-600 to-red-600"
        },
        {
            name: "Thor (Vercel)",
            role: "God of Deployment",
            description: "Summons the Bifrost to deploy your applications at lightning speed.",
            icon: Rocket,
            color: "from-yellow-400 to-orange-500"
        },
        {
            name: "Vision (Oumi)",
            role: "Insight & Analysis",
            description: "Phases through your codebase to detect bugs and vulnerabilities.",
            icon: Activity,
            color: "from-green-400 to-yellow-300"
        },
        {
            name: "Black Widow (CodeRabbit)",
            role: "Stealth Reviewer",
            description: "Infiltrates pull requests to provide lethal code reviews and insights.",
            icon: CheckCircle,
            color: "from-gray-800 to-red-600"
        },
        {
            name: "Doctor Strange (Together AI)",
            role: "Master of Summaries",
            description: "Views 14 million outcomes to generate the perfect project report.",
            icon: FileCode,
            color: "from-indigo-600 to-purple-600"
        },
    ];

    return (
        <section id="agents" className="relative py-16 md:py-24 bg-gradient-to-b from-black to-purple-900/20">
            <div className="container mx-auto px-4 md:px-6 lg:px-8">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeIn}
                    className="text-center mb-12"
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="inline-block rounded-full bg-gradient-to-r from-blue-500/20 via-red-500/20 to-yellow-500/20 px-4 py-2 text-sm mb-4 backdrop-blur-sm border border-blue-500/30 shadow-lg"
                    >
                        <Shield className="inline mr-2 h-4 w-4 text-blue-400" />
                        <span className="bg-gradient-to-r from-blue-400 via-red-400 to-yellow-400 bg-clip-text text-transparent font-semibold">
                            S.H.I.E.L.D. Roster
                        </span>
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-3xl md:text-5xl font-bold text-white mb-4"
                    >
                        Meet The{" "}
                        <span className="bg-gradient-to-r from-red-500 via-yellow-500 to-blue-500 bg-clip-text text-transparent animate-pulse">
                            Avengers of DevOps
                        </span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="text-gray-300 text-lg max-w-2xl mx-auto"
                    >
                        Six legendary heroes, each a master of their domain, united to automate your entire DevOps pipeline
                    </motion.p>
                </motion.div>

                <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                >
                    {agents.map((agent, index) => {
                        const agentTheme = MCUTheme.colors[agent.name.toLowerCase().includes('iron') ? 'ironMan' :
                            agent.name.toLowerCase().includes('captain') ? 'captainAmerica' :
                            agent.name.toLowerCase().includes('thor') ? 'thor' :
                            agent.name.toLowerCase().includes('vision') ? 'vision' :
                            agent.name.toLowerCase().includes('widow') ? 'blackWidow' :
                            'doctorStrange'];
                        
                        return (
                            <motion.div
                                key={index}
                                variants={itemFadeIn}
                                whileHover={{ 
                                    y: -15, 
                                    scale: 1.05,
                                    rotateY: 5,
                                }}
                                className="group relative overflow-hidden rounded-3xl border-2 border-white/20 bg-gradient-to-br from-black/80 to-black/60 backdrop-blur-sm p-6 shadow-2xl hover:shadow-[0_0_30px_rgba(255,215,0,0.3)] transition-all duration-500"
                                style={{
                                    boxShadow: `0 0 20px ${agentTheme.glow}40`,
                                }}
                            >
                                {/* MCU-style energy glow */}
                                <motion.div
                                    className={`absolute -right-20 -top-20 h-40 w-40 rounded-full bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-40 transition-opacity duration-500 blur-2xl`}
                                    animate={{
                                        scale: [1, 1.2, 1],
                                        opacity: [0.2, 0.4, 0.2],
                                    }}
                                    transition={{
                                        duration: 3,
                                        repeat: Infinity,
                                        ease: "easeInOut",
                                    }}
                                />
                                
                                {/* Shimmer effect on hover */}
                                <motion.div
                                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100"
                                    initial={{ x: "-100%" }}
                                    whileHover={{ x: "100%" }}
                                    transition={{ duration: 0.6 }}
                                />
                                
                                <div className="relative z-10">
                                    <motion.div
                                        className={`mb-4 inline-flex p-3 rounded-2xl bg-gradient-to-br ${agent.color} shadow-lg`}
                                        whileHover={{ 
                                            scale: 1.1,
                                            rotate: [0, -5, 5, 0],
                                        }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        <agent.icon className="h-6 w-6 text-white" />
                                    </motion.div>
                                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow-400 transition-colors">
                                        {agent.name}
                                    </h3>
                                    <p className="text-sm bg-gradient-to-r from-yellow-400 to-yellow-300 bg-clip-text text-transparent mb-3 font-semibold">
                                        {agent.role}
                                    </p>
                                    <p className="text-sm text-gray-300 leading-relaxed">{agent.description}</p>
                                </div>
                            </motion.div>
                        );
                    })}
                </motion.div>
            </div>
        </section>
    );
}

// --- Contact Section (Variant 2) ---

function ContactSection() {
    const [message, setMessage] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
            const recognition = new (window as any).webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            recognition.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setMessage(prev => prev + ' ' + transcript);
            };
            recognition.onend = () => setIsRecording(false);
            recognitionRef.current = recognition;
        }
    }, []);

    const handleVoiceInput = () => {
        if (isRecording) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
            setIsRecording(true);
        }
    };

    return (
        <section id="contact" className="relative py-16 md:py-24 bg-gradient-to-b from-purple-900/20 to-black">
            <div className="container mx-auto px-4 md:px-6 lg:px-8">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeIn}
                    className="max-w-4xl mx-auto"
                >
                    <div className="text-center mb-12">
                        <div className="inline-block rounded-full bg-purple-500/20 px-4 py-2 text-sm mb-4 backdrop-blur-sm border border-purple-500/30">
                            <Mail className="inline mr-2 h-4 w-4 text-purple-400" />
                            Get in Touch
                        </div>
                        <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                            Ready to <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">Automate</span>?
                        </h2>
                        <p className="text-gray-400 text-lg">
                            Start your autonomous DevOps journey today
                        </p>
                    </div>

                    <Card className="bg-black/50 backdrop-blur-sm border-purple-500/30 rounded-3xl p-8">
                        <form className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="text-sm font-medium text-white mb-2 block">GitHub Repository</label>
                                    <Input placeholder="https://github.com/user/repo" className="rounded-full bg-white/5 border-white/10 text-white" />
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-white mb-2 block">Vercel Project ID</label>
                                    <Input placeholder="prj_xxxxxxxxxxxxx" className="rounded-full bg-white/5 border-white/10 text-white" />
                                </div>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-white mb-2 block">Email</label>
                                <Input type="email" placeholder="your@email.com" className="rounded-full bg-white/5 border-white/10 text-white" />
                            </div>
                            <div>
                                <label className="text-sm font-medium text-white mb-2 block">Message</label>
                                <div className="flex space-x-2">
                                    <Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Tell us about your project..." className="rounded-3xl bg-white/5 border-white/10 text-white min-h-[120px] flex-1" />
                                    <Button onClick={handleVoiceInput} variant="outline" size="icon" className="rounded-full bg-white/10 border-white/30 text-white hover:bg-white/20 self-start">
                                        {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                                    </Button>
                                </div>
                            </div>
                            <Button size="lg" className="w-full rounded-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-semibold">
                                Start Autopilot
                                <Rocket className="ml-2 h-5 w-5" />
                            </Button>
                        </form>
                    </Card>
                </motion.div>
            </div>
        </section>
    );
}

// --- Sticky Footer (Variant 3) ---

const footerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.8,
            ease: "easeOut",
            staggerChildren: 0.1,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
        opacity: 1,
        x: 0,
        transition: { duration: 0.6, ease: "easeOut" },
    },
};

function StickyFooter() {
    const footerData = {
        sections: [
            { title: "Product", links: ["Features", "Pricing", "Documentation", "API"] },
            { title: "Company", links: ["About", "Blog", "Careers", "Contact"] },
            { title: "Resources", links: ["Community", "Support", "Status", "Security"] },
            { title: "Legal", links: ["Privacy", "Terms", "Cookies", "Licenses"] },
        ],
        social: [
            { href: "#", label: "GitHub", icon: <Github className="h-5 w-5" /> },
            { href: "#", label: "Twitter", icon: <Twitter className="h-5 w-5" /> },
            { href: "#", label: "LinkedIn", icon: <Linkedin className="h-5 w-5" /> },
        ],
        title: "DevOps Autopilot",
        subtitle: "Powered by AI Agents",
        copyright: "©2024 All rights reserved",
    };

    return (
        <div className="relative h-[70vh]" style={{ clipPath: "polygon(0% 0, 100% 0%, 100% 100%, 0 100%)" }}>
            <div className="relative h-[calc(100vh+70vh)] -top-[100vh]">
                <div className="h-[70vh] sticky top-[calc(100vh-70vh)]">
                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={footerVariants}
                        className="bg-gradient-to-br from-black via-gray-900 to-black py-6 md:py-12 px-4 md:px-12 h-full w-full flex flex-col justify-between relative overflow-hidden border-t border-white/10"
                    >
                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />

                        <motion.div
                            className="absolute top-0 right-0 w-48 h-48 md:w-96 md:h-96 bg-purple-500/10 rounded-full blur-3xl"
                            animate={{
                                scale: [1, 1.1, 1],
                                opacity: [0.3, 0.6, 0.3],
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                ease: "easeInOut",
                            }}
                        />

                        <motion.div variants={footerVariants} className="relative z-10">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-12 lg:gap-20">
                                {footerData.sections.map((section, index) => (
                                    <motion.div key={section.title} variants={itemVariants} className="flex flex-col gap-2">
                                        <h3 className="mb-2 uppercase text-gray-400 text-xs font-semibold tracking-wider border-b border-gray-800 pb-1">
                                            {section.title}
                                        </h3>
                                        {section.links.map((link) => (
                                            <a
                                                key={link}
                                                href="#"
                                                className="text-gray-500 hover:text-white transition-colors duration-300 font-sans text-xs md:text-sm"
                                            >
                                                {link}
                                            </a>
                                        ))}
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.8, duration: 0.8, ease: "easeOut" }}
                            className="flex flex-col md:flex-row justify-between items-start md:items-end relative z-10 gap-4 md:gap-6 mt-6"
                        >
                            <div className="flex-1">
                                <h1 className="text-[12vw] md:text-[10vw] lg:text-[8vw] xl:text-[6vw] leading-[0.8] font-serif bg-gradient-to-r from-white via-gray-400 to-white/60 bg-clip-text text-transparent">
                                    {footerData.title}
                                </h1>
                                <div className="flex items-center gap-3 md:gap-4 mt-3 md:mt-4">
                                    <div className="w-8 md:w-12 h-0.5 bg-gradient-to-r from-purple-500 to-blue-500" />
                                    <p className="text-gray-400 text-xs md:text-sm font-sans">
                                        {footerData.subtitle}
                                    </p>
                                </div>
                            </div>

                            <div className="text-left md:text-right">
                                <p className="text-gray-500 text-xs md:text-sm mb-2 md:mb-3">
                                    {footerData.copyright}
                                </p>
                                <div className="flex gap-2 md:gap-3">
                                    {footerData.social.map((social) => (
                                        <a
                                            key={social.label}
                                            href={social.href}
                                            className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-gray-800 hover:bg-gradient-to-r hover:from-purple-500 hover:to-blue-500 flex items-center justify-center transition-colors duration-300 group"
                                            aria-label={social.label}
                                        >
                                            <span className="text-xs md:text-sm font-bold text-gray-400 group-hover:text-white">
                                                {social.icon}
                                            </span>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}

// --- Main Combined Landing Page ---

export default function CombinedLanding() {
    const screenshotRef = useRef<HTMLDivElement>(null);
    const heroContentRef = useRef<HTMLDivElement>(null);
    const [demoMode, setDemoMode] = useState(false);
    const [workflowStatus, setWorkflowStatus] = useState<DemoStatus | null>(null);
    const [executionId, setExecutionId] = useState<string | undefined>(undefined);
    const [repoUrl, setRepoUrl] = useState<string>("");

    useEffect(() => {
        const handleScroll = () => {
            if (screenshotRef.current && heroContentRef.current) {
                requestAnimationFrame(() => {
                    const scrollPosition = window.pageYOffset;
                    if (screenshotRef.current) {
                        screenshotRef.current.style.transform = `translateY(-${scrollPosition * 0.5}px)`;
                    }

                    const maxScroll = 400;
                    const opacity = 1 - Math.min(scrollPosition / maxScroll, 1);
                    if (heroContentRef.current) {
                        heroContentRef.current.style.opacity = opacity.toString();
                    }
                });
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (demoMode) {
            interval = setInterval(async () => {
                const status = await getDemoStatus();
                if (status) {
                    setWorkflowStatus(status);
                    if (!status.is_active) {
                        setDemoMode(false);
                    }
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [demoMode]);

    const handleDemoStart = async (url: string) => {
        setDemoMode(true);
        setRepoUrl(url);
        const result = await startDemo();
        // Extract execution ID if available
        if (result && 'execution_id' in result) {
            setExecutionId(result.execution_id as string);
        }
        // Scroll to dashboard
        screenshotRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    return (
        <div className="relative bg-black min-h-screen">
            <Navbar />

            <div className="relative min-h-screen">
                <div className="absolute inset-0 z-0 pointer-events-auto">
                    <HeroSplineBackground />
                </div>

                <div ref={heroContentRef} style={{
                    position: 'absolute', top: 0, left: 0, width: '100%', height: '100vh',
                    display: 'flex', justifyContent: 'flex-start', alignItems: 'center', zIndex: 10, pointerEvents: 'none'
                }}>
                    <div className="container mx-auto">
                        <HeroContent onStartDemo={handleDemoStart} isDemoActive={demoMode} />
                    </div>
                </div>
            </div>

            <div className="bg-black relative z-10" style={{ marginTop: '-10vh' }}>
                <section className="relative z-10 container mx-auto px-4 md:px-6 lg:px-8 mt-11 md:mt-12">
                    <div ref={screenshotRef} className="bg-gradient-to-br from-purple-900/20 to-black rounded-3xl overflow-hidden shadow-2xl border border-purple-500/30 w-full md:w-[80%] lg:w-[70%] mx-auto">
                        <div className="p-8">
                            {/* Replaced the small mock dashboard with the full Agent Workflow Dashboard */}
                            <AgentWorkflowDashboard 
                                workflowStatus={workflowStatus} 
                                executionId={executionId}
                                repoUrl={repoUrl}
                            />
                        </div>
                    </div>
                </section>

                <FeaturesSection />
                <AgentsSection />
                <ContactSection />
                <StickyFooter />
            </div>
        </div>
    );
}
