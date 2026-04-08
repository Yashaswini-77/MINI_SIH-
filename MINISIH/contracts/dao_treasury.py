from __future__ import annotations

from pyteal import *

APPROVAL_BPS_DENOMINATOR = Int(10000)
ZERO_ADDRESS = Bytes("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ")


def proposal_box_name(proposal_id: Expr, suffix: str) -> Expr:
    return Concat(Bytes("p:"), Itob(proposal_id), Bytes(":"), Bytes(suffix))


def vote_box_name(proposal_id: Expr, voter: Expr) -> Expr:
    return Concat(Bytes("v:"), Itob(proposal_id), Bytes(":"), voter)


def box_bytes(name: Expr) -> Expr:
    return App.box_get(name).value()


def box_uint(name: Expr) -> Expr:
    return Btoi(box_bytes(name))


def create_proposal() -> Expr:
    proposal_id = ScratchVar(TealType.uint64)
    amount = ScratchVar(TealType.uint64)
    quorum = ScratchVar(TealType.uint64)
    approval_bps = ScratchVar(TealType.uint64)
    duration = ScratchVar(TealType.uint64)

    return Seq(
        Assert(Txn.application_args.length() == Int(8)),
        amount.store(Btoi(Txn.application_args[3])),
        quorum.store(Btoi(Txn.application_args[5])),
        approval_bps.store(Btoi(Txn.application_args[6])),
        duration.store(Btoi(Txn.application_args[7])),
        Assert(Len(Txn.application_args[1]) > Int(0)),
        Assert(Len(Txn.application_args[2]) > Int(0)),
        Assert(amount.load() > Int(0)),
        Assert(Len(Txn.application_args[4]) == Int(32)),
        Assert(Txn.application_args[4] != ZERO_ADDRESS),
        Assert(quorum.load() > Int(0)),
        Assert(approval_bps.load() > Int(0)),
        Assert(approval_bps.load() <= APPROVAL_BPS_DENOMINATOR),
        Assert(duration.load() > Int(0)),
        proposal_id.store(App.globalGet(Bytes("next_id"))),
        App.box_put(proposal_box_name(proposal_id.load(), "title"), Txn.application_args[1]),
        App.box_put(proposal_box_name(proposal_id.load(), "description"), Txn.application_args[2]),
        App.box_put(proposal_box_name(proposal_id.load(), "amount"), Itob(amount.load())),
        App.box_put(proposal_box_name(proposal_id.load(), "recipient"), Txn.application_args[4]),
        App.box_put(proposal_box_name(proposal_id.load(), "creator"), Txn.sender()),
        App.box_put(proposal_box_name(proposal_id.load(), "start"), Itob(Global.round())),
        App.box_put(proposal_box_name(proposal_id.load(), "end"), Itob(Global.round() + duration.load())),
        App.box_put(proposal_box_name(proposal_id.load(), "quorum"), Itob(quorum.load())),
        App.box_put(proposal_box_name(proposal_id.load(), "approval"), Itob(approval_bps.load())),
        App.box_put(proposal_box_name(proposal_id.load(), "yes"), Itob(Int(0))),
        App.box_put(proposal_box_name(proposal_id.load(), "no"), Itob(Int(0))),
        App.box_put(proposal_box_name(proposal_id.load(), "executed"), Itob(Int(0))),
        App.box_put(proposal_box_name(proposal_id.load(), "closed"), Itob(Int(0))),
        App.globalPut(Bytes("next_id"), proposal_id.load() + Int(1)),
        Approve(),
    )


def vote() -> Expr:
    proposal_id = ScratchVar(TealType.uint64)
    support = ScratchVar(TealType.uint64)
    end_round = ScratchVar(TealType.uint64)
    vote_key = ScratchVar(TealType.bytes)
    yes_count = ScratchVar(TealType.uint64)
    no_count = ScratchVar(TealType.uint64)

    return Seq(
        Assert(Txn.application_args.length() == Int(3)),
        proposal_id.store(Btoi(Txn.application_args[1])),
        support.store(Btoi(Txn.application_args[2])),
        Assert(Or(support.load() == Int(0), support.load() == Int(1))),
        end_round.store(box_uint(proposal_box_name(proposal_id.load(), "end"))),
        Assert(Global.round() <= end_round.load()),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "executed")) == Int(0)),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "closed")) == Int(0)),
        vote_key.store(vote_box_name(proposal_id.load(), Txn.sender())),
        Assert(Not(App.box_get(vote_key.load()).hasValue())),
        App.box_put(vote_key.load(), Itob(support.load())),
        yes_count.store(box_uint(proposal_box_name(proposal_id.load(), "yes"))),
        no_count.store(box_uint(proposal_box_name(proposal_id.load(), "no"))),
        If(support.load() == Int(1))
        .Then(App.box_put(proposal_box_name(proposal_id.load(), "yes"), Itob(yes_count.load() + Int(1))))
        .Else(App.box_put(proposal_box_name(proposal_id.load(), "no"), Itob(no_count.load() + Int(1)))),
        Approve(),
    )


def execute_release() -> Expr:
    proposal_id = ScratchVar(TealType.uint64)
    amount = ScratchVar(TealType.uint64)
    recipient = ScratchVar(TealType.bytes)
    quorum = ScratchVar(TealType.uint64)
    approval_bps = ScratchVar(TealType.uint64)
    yes_count = ScratchVar(TealType.uint64)
    no_count = ScratchVar(TealType.uint64)
    total_votes = ScratchVar(TealType.uint64)
    end_round = ScratchVar(TealType.uint64)

    return Seq(
        Assert(Txn.application_args.length() == Int(2)),
        proposal_id.store(Btoi(Txn.application_args[1])),
        amount.store(box_uint(proposal_box_name(proposal_id.load(), "amount"))),
        recipient.store(box_bytes(proposal_box_name(proposal_id.load(), "recipient"))),
        quorum.store(box_uint(proposal_box_name(proposal_id.load(), "quorum"))),
        approval_bps.store(box_uint(proposal_box_name(proposal_id.load(), "approval"))),
        yes_count.store(box_uint(proposal_box_name(proposal_id.load(), "yes"))),
        no_count.store(box_uint(proposal_box_name(proposal_id.load(), "no"))),
        end_round.store(box_uint(proposal_box_name(proposal_id.load(), "end"))),
        Assert(Global.round() > end_round.load()),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "executed")) == Int(0)),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "closed")) == Int(0)),
        total_votes.store(yes_count.load() + no_count.load()),
        Assert(total_votes.load() >= quorum.load()),
        Assert(yes_count.load() * APPROVAL_BPS_DENOMINATOR >= total_votes.load() * approval_bps.load()),
        Assert(Len(recipient.load()) == Int(32)),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: recipient.load(),
                TxnField.amount: amount.load(),
            }
        ),
        InnerTxnBuilder.Submit(),
        App.box_put(proposal_box_name(proposal_id.load(), "executed"), Itob(Int(1))),
        App.box_put(proposal_box_name(proposal_id.load(), "closed"), Itob(Int(1))),
        Approve(),
    )


def close_failed() -> Expr:
    proposal_id = ScratchVar(TealType.uint64)
    end_round = ScratchVar(TealType.uint64)
    yes_count = ScratchVar(TealType.uint64)
    no_count = ScratchVar(TealType.uint64)
    quorum = ScratchVar(TealType.uint64)

    return Seq(
        Assert(Txn.application_args.length() == Int(2)),
        proposal_id.store(Btoi(Txn.application_args[1])),
        end_round.store(box_uint(proposal_box_name(proposal_id.load(), "end"))),
        Assert(Global.round() > end_round.load()),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "executed")) == Int(0)),
        Assert(box_uint(proposal_box_name(proposal_id.load(), "closed")) == Int(0)),
        yes_count.store(box_uint(proposal_box_name(proposal_id.load(), "yes"))),
        no_count.store(box_uint(proposal_box_name(proposal_id.load(), "no"))),
        quorum.store(box_uint(proposal_box_name(proposal_id.load(), "quorum"))),
        Assert(yes_count.load() + no_count.load() < quorum.load()),
        App.box_put(proposal_box_name(proposal_id.load(), "closed"), Itob(Int(1))),
        Approve(),
    )


def approval_program() -> Expr:
    on_create = Seq(
        App.globalPut(Bytes("admin"), Txn.sender()),
        App.globalPut(Bytes("next_id"), Int(1)),
        App.globalPut(Bytes("default_quorum"), Int(3)),
        App.globalPut(Bytes("default_approval_bps"), Int(5000)),
        App.globalPut(Bytes("proposal_lifetime"), Int(5760)),
        Approve(),
    )

    on_noop = Cond(
        [Txn.application_args[0] == Bytes("create_proposal"), create_proposal()],
        [Txn.application_args[0] == Bytes("vote"), vote()],
        [Txn.application_args[0] == Bytes("execute"), execute_release()],
        [Txn.application_args[0] == Bytes("close_failed"), close_failed()],
    )

    return Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, on_noop],
    )


def clear_state_program() -> Expr:
    return Approve()


def compile_contract() -> tuple[str, str]:
    approval_teal = compileTeal(approval_program(), Mode.Application, version=10)
    clear_teal = compileTeal(clear_state_program(), Mode.Application, version=10)
    return approval_teal, clear_teal


if __name__ == "__main__":
    approval, clear = compile_contract()
    print("--- APPROVAL ---")
    print(approval)
    print("--- CLEAR ---")
    print(clear)
