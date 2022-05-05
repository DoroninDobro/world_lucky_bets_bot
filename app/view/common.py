from app.models.enum.user_status import WorkerStatus

boolean_emoji = {True: "✅", False: "🚫"}

USER_STATUS_NAME = {
    WorkerStatus.WIN_PERCENT: "💸 percent by winning",
    WorkerStatus.BET_PERCENT: "💰 percent by bet",
    WorkerStatus.SALARY: "💵 salary",
    None: "",
}
