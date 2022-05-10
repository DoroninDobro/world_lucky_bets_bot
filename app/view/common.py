from app.models.enum.salary_type import SalaryType

boolean_emoji = {True: "✅", False: "🚫"}

USER_STATUS_NAME = {
    SalaryType.WIN_PERCENT: "💸 percent by winning",
    SalaryType.BET_PERCENT: "💰 percent by bet",
    SalaryType.SALARY: "💵 salary",
    None: "",
}
