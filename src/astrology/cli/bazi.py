"""八字排盘命令。"""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time, location_options, ut_option,
    resolve_location, resolve_time,
)
from ..chinese.bazi import calculate_bazi, get_bazi_summary
from ..chinese.formatting import (
    format_bazi, format_bazi_compact, format_relations_analysis,
    format_dayun, format_liunian, format_full_report,
)
from ..chinese.dayun import calculate_dayun_simple
from ..chinese.liunian import get_liunian_range


@click.command()
@click.option("--date", "date_val", required=True, callback=parse_date, help="出生日期 YYYY-MM-DD。")
@click.option("--time", "time_val", required=True, callback=parse_time, help="出生时间 HH:MM[:SS]（本地时间）。")
@location_options
@click.option("--true-solar/--no-true-solar", default=True, help="使用真太阳时（默认开启）。")
@click.option("--split-zi", is_flag=True, default=False, help="分早晚子时（默认不分）。")
@click.option("--sex", type=click.Choice(["male", "female"], case_sensitive=False), 
              default="male", help="性别（用于大运计算）。")
@click.option("--year-start", type=int, default=None, help="流年起始年份（默认当前年）。")
@click.option("--year-end", type=int, default=None, help="流年结束年份（默认起始+10）。")
@click.option("--compact", is_flag=True, help="紧凑输出。")
@click.option("--relations", is_flag=True, help="显示地支关系分析。")
@click.option("--dayun", is_flag=True, help="显示大运。")
@click.option("--liunian", is_flag=True, help="显示流年。")
@click.pass_context
def bazi(
    ctx, date_val, time_val, location, city, 
    true_solar, split_zi, sex,
    year_start, year_end,
    compact, relations, dayun, liunian
):
    """
    八字排盘。
    
    示例:
        uv run astro bazi --date 1990-01-15 --time 08:00 --city "Beijing"
        uv run astro bazi --date 1990-01-15 --time 08:00 --location "39.9,116.4" --relations --dayun
    """
    loc = resolve_location(location, city)
    if loc is None:
        raise click.UsageError("请指定 --location 或 --city")
    
    # 解析时间（不使用 UT 选项，八字用本地时间）
    y, m, d, hour, _ = resolve_time(date_val, time_val, loc, ut_flag=False)
    
    # 计算八字
    bazi_obj = calculate_bazi(
        year=y, month=m, day=d, hour=hour,
        location=loc,
        use_true_solar_time=true_solar,
        use_split_zi=split_zi,
    )
    
    # 紧凑输出
    if compact:
        click.echo(format_bazi_compact(bazi_obj))
        return
    
    # 完整输出
    click.echo(format_bazi(bazi_obj))
    
    # 地支关系
    if relations:
        click.echo()
        click.echo(format_relations_analysis(bazi_obj))
    
    # 大运
    if dayun:
        is_male = sex == "male"
        dy_list = calculate_dayun_simple(
            swe.julday(y, m, d, hour),
            bazi_obj.year_pillar.stem_index,
            bazi_obj.month_pillar.stem_index,
            bazi_obj.month_pillar.branch_index,
            is_male=is_male,
        )
        click.echo()
        click.echo(format_dayun(dy_list))
    
    # 流年
    if liunian:
        if year_start is None:
            import datetime
            year_start = datetime.datetime.now().year
        if year_end is None:
            year_end = year_start + 10
        
        ln_list = get_liunian_range(year_start, year_end)
        click.echo()
        click.echo(format_liunian(ln_list))


# 需要导入 swe
import swisseph as swe
