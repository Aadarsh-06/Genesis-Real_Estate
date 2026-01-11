import React from "react";

export default function About() {
    return (
        <div className="max-w-4xl mx-auto py-12 px-6 text-slate-200 animate-fade-in">
            {/* Header */}
            <div className="mb-12 text-center">
                <h1 className="text-3xl font-bold text-[#00d4ff] mb-4">Platform Architecture & Philosophy</h1>
                <p className="text-slate-400 max-w-2xl mx-auto">
                    Built to provide clarity on buy vs rent decisions using verifiable financial models and explainable AI-driven insights.
                </p>
            </div>

            <div className="space-y-12">
                {/* 1. What This Platform Does */}
                <section className="glass-card p-8 rounded-2xl border border-[#00d4ff]/10">
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <span className="text-[#00d4ff]">01.</span> What This Platform Does
                    </h2>
                    <p className="text-slate-300 leading-relaxed">
                        This platform helps users distinguish whether buying or renting makes more financial sense for specific properties.
                        It utilizes real estate data combined with verified financial calculations to compute outcomes like wealth accumulation
                        and break-even periods. The focus is strictly on providing decision clarity through data-backed analysis,
                        rather than attempting to predict future market fluctuations.
                    </p>
                </section>

                {/* 2. Why This Is Different */}
                <section className="glass-card p-8 rounded-2xl border border-[#00d4ff]/10">
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <span className="text-[#00d4ff]">02.</span> Why This Is Different
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div>
                            <p className="text-slate-300 leading-relaxed mb-4">
                                Unlike traditional AI tools that generate answers probabilistically, this system explains decisions that have
                                already been verified by deterministic financial logic.
                            </p>
                            <p className="text-slate-300 leading-relaxed">
                                The core calculations for "Buy" or "Rent" decisions are performed by rigid algorithms, not the language model.
                                The AI's role is strictly limited to explaining <em>why</em> a decision was made based on the computed data.
                            </p>
                        </div>
                        <div className="bg-[#0a1628]/50 p-6 rounded-xl border border-[#00d4ff]/20 flex flex-col justify-center">
                            <div className="flex items-center gap-3 mb-2">
                                <span className="text-emerald-400 font-mono">✓</span>
                                <span className="text-sm">Deterministic Financial Models</span>
                            </div>
                            <div className="flex items-center gap-3 mb-2">
                                <span className="text-emerald-400 font-mono">✓</span>
                                <span className="text-sm">Auditable Logic</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="text-emerald-400 font-mono">✓</span>
                                <span className="text-sm">AI as Explainer, not Decider</span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 3. How the System Works */}
                <section className="glass-card p-8 rounded-2xl border border-[#00d4ff]/10">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <span className="text-[#00d4ff]">03.</span> How the System Works
                    </h2>
                    <div className="relative">
                        {/* Connecting Line (Desktop) */}
                        <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-[#00d4ff]/20 -z-10 transform -translate-y-1/2"></div>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            {[
                                { title: "Data Ingestion", desc: "Property data is analyzed using fixed financial models." },
                                { title: "Computation", desc: "Buy vs Rent outcomes are computed deterministically." },
                                { title: "Retrieval", desc: "Explanation records are stored and retrieved via semantic search." },
                                { title: "Presentation", desc: "AI presents clear, human-readable explanations." }
                            ].map((step, idx) => (
                                <div key={idx} className="bg-[#0a1628] p-5 rounded-xl border border-[#00d4ff]/20 relative">
                                    <div className="w-8 h-8 rounded-full bg-[#00d4ff]/10 text-[#00d4ff] flex items-center justify-center text-sm font-bold mb-3 border border-[#00d4ff]/30">
                                        {idx + 1}
                                    </div>
                                    <h3 className="font-bold text-white mb-2">{step.title}</h3>
                                    <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* 4. Commitment to Transparency */}
                <section className="glass-card p-8 rounded-2xl border border-[#00d4ff]/10">
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <span className="text-[#00d4ff]">04.</span> Commitment to Transparency
                    </h2>
                    <p className="text-slate-300 leading-relaxed border-l-2 border-[#00d4ff] pl-6 py-1">
                        Every recommendation can be challenged. Users can view the assumptions behind each calculation and ask
                        "what would flip this decision?" to understand the sensitivity of the outcome. We ensure users
                        understand not just the result, but its robustness and dependencies.
                    </p>
                </section>

                {/* 5. Closing */}
                <div className="text-center py-8">


                </div>
            </div>
        </div>
    );
}
