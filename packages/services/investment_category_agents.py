from packages.domain.investment import InvestmentThesis
from packages.domain.investment_agents import AgentOpinion, AgentStance


def build_swing_bull_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="swing_bull_agent",
        stance=AgentStance.bullish,
        confidence=min(max(engine_output.get("confidence_score", 50) / 100, 0), 1),
        thesis=f"Swing bull case on {thesis.ticker} is supported by structured upside and trend continuation.",
        supporting_points=[
            "Trend-following setup is defined.",
            "Entry, target, and invalidation can be tracked.",
            "Catalyst path can support continuation.",
        ],
        risk_points=[],
        evidence_gaps=[] if thesis.catalysts else ["Need a clearer timing catalyst."],
    )


def build_swing_bear_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="swing_bear_agent",
        stance=AgentStance.bearish,
        confidence=min(max(1 - (engine_output.get("confidence_score", 50) / 100), 0), 1),
        thesis=f"Swing bear case on {thesis.ticker} is that the setup may be fragile or crowded.",
        supporting_points=[],
        risk_points=[
            "Momentum can reverse quickly around catalyst windows.",
            "Stops may be too obvious in crowded trend setups.",
        ] + [f"Risk flag: {flag}" for flag in thesis.risk_flags],
        evidence_gaps=[] if thesis.invalidation else ["Need explicit invalidation discipline."],
    )


def build_options_bull_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="options_bull_agent",
        stance=AgentStance.bullish,
        confidence=min(max(engine_output.get("confidence_score", 50) / 100, 0), 1),
        thesis=f"Options bull case on {thesis.ticker} is that defined-risk structure improves payoff asymmetry.",
        supporting_points=[
            "Structure can cap downside while preserving upside.",
            "Directional thesis can be expressed with better capital efficiency.",
        ],
        risk_points=[],
        evidence_gaps=[] if thesis.invalidation else ["Need clearer invalidation on the underlying."],
    )


def build_options_bear_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="options_bear_agent",
        stance=AgentStance.bearish,
        confidence=min(max(1 - (engine_output.get("confidence_score", 50) / 100), 0), 1),
        thesis=f"Options bear case on {thesis.ticker} is that volatility or structure may weaken the edge.",
        supporting_points=[],
        risk_points=[
            "Volatility can stay elevated or collapse unexpectedly.",
            "Time decay can erode a weak directional thesis.",
        ] + [f"Risk flag: {flag}" for flag in thesis.risk_flags],
        evidence_gaps=[] if thesis.catalysts else ["Need clearer event timing for structure selection."],
    )


def build_crypto_bull_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="crypto_bull_agent",
        stance=AgentStance.bullish,
        confidence=min(max(engine_output.get("confidence_score", 50) / 100, 0), 1),
        thesis=f"Crypto bull case on {thesis.ticker} is that regime and narrative remain supportive.",
        supporting_points=[
            "Crypto setup can benefit from regime persistence.",
            "Narrative and liquidity can reinforce continuation.",
        ],
        risk_points=[],
        evidence_gaps=[] if thesis.catalysts else ["Need clearer catalyst map for crypto timing."],
    )


def build_crypto_bear_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="crypto_bear_agent",
        stance=AgentStance.bearish,
        confidence=min(max(1 - (engine_output.get("confidence_score", 50) / 100), 0), 1),
        thesis=f"Crypto bear case on {thesis.ticker} is that liquidity and regime can shift abruptly.",
        supporting_points=[],
        risk_points=[
            "Risk-on regime can reverse abruptly.",
            "Narrative trades can unwind quickly when liquidity thins.",
        ] + [f"Risk flag: {flag}" for flag in thesis.risk_flags],
        evidence_gaps=[] if thesis.invalidation else ["Need clearer downside discipline for crypto volatility."],
    )


def build_prediction_bull_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="prediction_bull_agent",
        stance=AgentStance.bullish,
        confidence=min(max(engine_output.get("confidence_score", 50) / 100, 0), 1),
        thesis=f"Prediction bull case on {thesis.ticker} is that estimated probability exceeds market pricing with acceptable clarity.",
        supporting_points=[
            "Event edge appears measurable.",
            "Settlement rules can be tracked explicitly.",
        ],
        risk_points=[],
        evidence_gaps=[] if thesis.catalysts else ["Need clearer event map or trigger tree."],
    )


def build_prediction_bear_opinion(thesis: InvestmentThesis, engine_output: dict) -> AgentOpinion:
    return AgentOpinion(
        agent_name="prediction_bear_agent",
        stance=AgentStance.bearish,
        confidence=min(max(1 - (engine_output.get("confidence_score", 50) / 100), 0), 1),
        thesis=f"Prediction bear case on {thesis.ticker} is that settlement ambiguity or weak edge can erase expected value.",
        supporting_points=[],
        risk_points=[
            "Edge may be too small after friction and uncertainty.",
            "Settlement interpretation can distort apparent mispricing.",
        ] + [f"Risk flag: {flag}" for flag in thesis.risk_flags],
        evidence_gaps=[] if thesis.invalidation else ["Need clearer invalidation or no-trade threshold."],
    )
