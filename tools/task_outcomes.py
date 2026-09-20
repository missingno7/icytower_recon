"""CLI contract: only completed candidate proof rejection may block a source task."""
CANDIDATE_REJECTED_EXIT = 10


class CandidateRejected(ValueError):
    """A fresh candidate failed an explicit comparison/declaration predicate."""


def candidate_check(check, *args, **kwargs):
    """Adapt a known proof predicate; never wrap compilation or input validation."""
    try:
        return check(*args, **kwargs)
    except ValueError as exc:
        raise CandidateRejected(str(exc)) from exc


def fast_exit(state):
    """Success means a promotable proof state, not necessarily exact raw bytes."""
    return 0 if state in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED') else CANDIDATE_REJECTED_EXIT
