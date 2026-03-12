"""八字行运分析命令 —— 查看当前或指定时间的运势。"""

from __future__ import annotations

from datetime import datetime

import click

from .common import parse_date, parse_time, location_options, resolve_location
from ..chinese.bazi import calculate_bazi
from ..chinese.transit import analyze_period, format_period, format_period_compact
from ..chinese.dayun import calculate_dayun_simple


@click.command(name="period")
@click.option("--natal-date", "date_val", required=True, callback=parse_date, help="出生日期 YYYY-MM-DD。")
@click.option("--natal-time", "time_val", required=True, callback=parse_time, help="出生时间 HH:MM[:SS]（本地时间）。")
@location_options
@click.option("--gender", type=click.Choice(["male", "female"], case_sensitive=False), 
              default="male", help="性别（用于大运计算）。")
@click.option("--year", type=int, default=None, help="目标年份（默认当前年）。")
@click.option("--month", type=int, default=None, help="目标月份（默认当前月）。")
@click.option("--day", type=int, default=None, help="目标日期（默认当前日）。")
@click.option("--compact", is_flag=True, help="紧凑输出。")
@click.pass_context
def bazi_period(
    ctx, date_val, time_val, location, city,
    gender, year, month, day, compact
):
    """
    八字行运分析 —— 查看大运、流年、流月与原局的关系。
    
    默认显示当前时间的运势，可指定年月日查看特定时间。
    
    示例:
        # 查看当前运势
        uv run astro bazi period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing"
        
        # 查看2026年运势
        uv run astro bazi period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing" --year 2026
        
        # 查看2026年3月运势
        uv run astro bazi period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing" --year 2026 --month 3
    """
    import swisseph as swe
    
    loc = resolve_location(location, city)
    if loc is None:
        raise click.UsageError("请指定 --location 或 --city")
    
    # 计算原局八字（不用真太阳时，保持与 bazi 命令一致）
    y, m, d = date_val
    hour = time_val
    bazi_obj = calculate_bazi(
        year=y, month=m, day=d, hour=hour,
        location=loc,
        use_true_solar_time=False,
        use_split_zi=False,
    )
    
    # 确定目标时间（默认当前）
    now = datetime.now()
    target_year = year if year is not None else now.year
    target_month = month  # None 表示不显示流月
    target_day = day      # None 表示不显示流日
    
    # 如果没指定年月日但也没指定具体哪个，默认显示到流月
    if year is None and month is None and day is None:
        target_month = now.month
        target_day = now.day
    elif year is not None and month is None:
        # 指定了年没指定月，显示整年（不显示流月流日）
        target_month = None
        target_day = None
    elif year is not None and month is not None and day is None:
        # 指定了年月没指定日，显示到流月
        target_day = None
    
    # 计算大运
    is_male = gender == "male"
    jd = swe.julday(y, m, d, hour)
    dayun_list = calculate_dayun_simple(
        jd,
        bazi_obj.year_pillar.stem_index,
        bazi_obj.month_pillar.stem_index,
        bazi_obj.month_pillar.branch_index,
        is_male=is_male,
    )
    
    # 分析行运
    period = analyze_period(
        bazi_obj,
        year=target_year,
        month=target_month,
        day=target_day,
        dayun_list=dayun_list,
    )
    
    # 输出
    if compact:
        click.echo(format_period_compact(period))
    else:
        click.echo(format_period(period))
