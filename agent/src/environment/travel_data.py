"""
环境交互模块 (Environment)

本模块提供旅游数据的查询和工具调用功能，作为Agent与外部环境交互的接口。
采用工具注册模式，支持动态注册和调用旅游相关工具。

主要组件:
- TravelData: 旅游数据环境类，提供城市搜索、景点查询、预算计算等功能

功能特点:
- 根据兴趣、预算、季节搜索匹配的城市
- 查询城市的景点详细信息
- 计算旅游预算
- 支持地区级别的城市搜索

使用示例:
    from config.config_manager import ConfigManager
    from environment.travel_data import TravelData

    config = ConfigManager("config/llm_config.yaml")
    env = TravelData(config)

    # 搜索城市
    result = env.search_cities(interests=["美食", "历史文化"])

    # 查询景点
    result = env.query_attractions(["北京", "西安"])

    # 计算预算
    result = env.calculate_budget("北京", days=3)
"""

from typing import Dict, Any, List, Optional


class TravelData:
    """
    旅游数据环境类

    作为Agent执行环境，提供旅游相关的数据查询和工具调用功能。
    封装了ConfigManager的配置访问，提供更友好的工具接口。

    工具列表:
        - search_cities: 根据条件搜索城市
        - query_attractions: 查询景点信息
        - calculate_budget: 计算旅游预算
        - get_city_info: 获取城市详细信息

    属性:
        config_manager: ConfigManager 配置管理器实例
        tools: Dict[str, callable] 已注册的工具字典
    """

    def __init__(self, config_manager):
        """
        初始化旅游数据环境

        Args:
            config_manager: ConfigManager 配置管理器实例
        """
        self.config_manager = config_manager
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, callable]:
        """
        注册可用工具

        Returns:
            Dict[str, callable]: 工具名称到工具函数的映射
        """
        return {
            "search_cities": self.search_cities,
            "query_attractions": self.query_attractions,
            "calculate_budget": self.calculate_budget,
            "get_city_info": self.get_city_info
        }

    def search_cities(self, interests: List[str] = None,
                     budget: tuple = None,
                     season: str = None) -> Dict[str, Any]:
        """
        根据兴趣、预算、季节搜索匹配的城市

        根据用户提供的筛选条件，对所有内置城市进行匹配评分，
        返回按匹配度排序的城市列表。

        评分规则:
            - 兴趣匹配: +30分/个
            - 预算适合: +20分
            - 预算较低: +10分
            - 季节适宜: +15分

        Args:
            interests: List[str] 兴趣标签列表，如["美食", "历史文化"]
            budget: tuple 预算范围 (min, max)，如 (300, 800)
            season: str 出行季节，如"春季"、"夏季"

        Returns:
            Dict[str, Any]: 搜索结果
                - success: bool 是否成功
                - cities: List[Dict] 匹配的城市列表
                - count: int 匹配数量

        示例:
            >>> env.search_cities(interests=["美食"], budget=(300, 600))
            {
                "success": True,
                "cities": [
                    {
                        "city": "成都",
                        "score": 80,
                        "info": {...},
                        "match_reasons": ["符合美食兴趣", "预算适合"]
                    }
                ],
                "count": 1
            }
        """
        all_cities = self.config_manager.get_all_cities()
        matched_cities = []

        for city_name in all_cities:
            city_info = self.config_manager.get_city_info(city_name)
            if not city_info:
                continue

            score = 0
            match_reasons = []

            # 兴趣匹配评分
            if interests:
                city_tags = city_info.get('tags', [])
                for interest in interests:
                    if interest in city_tags or any(interest in tag for tag in city_tags):
                        score += 30
                        match_reasons.append(f"符合{interest}兴趣")

            # 预算匹配评分
            if budget:
                avg_budget = city_info.get('avg_budget_per_day', 0)
                if budget[0] <= avg_budget <= budget[1]:
                    score += 20
                    match_reasons.append("预算适合")
                elif avg_budget < budget[1]:
                    score += 10

            # 季节匹配评分
            if season:
                best_seasons = city_info.get('best_season', [])
                if season in best_seasons:
                    score += 15
                    match_reasons.append("季节适宜")

            # 如果没有筛选条件，返回默认城市
            if not interests and not budget and not season:
                score = 50

            if score > 0:
                matched_cities.append({
                    "city": city_name,
                    "score": score,
                    "info": city_info,
                    "match_reasons": match_reasons
                })

        # 按分数降序排序
        matched_cities.sort(key=lambda x: x['score'], reverse=True)

        return {
            "success": True,
            "cities": matched_cities,
            "count": len(matched_cities)
        }

    def query_attractions(self, cities: List[str]) -> Dict[str, Any]:
        """
        查询指定城市的景点信息

        Args:
            cities: List[str] 城市名称列表

        Returns:
            Dict[str, Any]: 查询结果
                - success: bool 是否成功
                - data: Dict[str, Dict] 城市景点信息字典
                - cities_count: int 查询的城市数量

        数据结构:
            {
                "北京": {
                    "attractions": [...],  # 景点列表
                    "avg_budget_per_day": 500,  # 日均预算
                    "recommended_days": 4  # 推荐天数
                }
            }
        """
        result = {}

        for city_name in cities:
            city_info = self.config_manager.get_city_info(city_name)
            if city_info:
                result[city_name] = {
                    "attractions": city_info.get('attractions', []),
                    "avg_budget_per_day": city_info.get('avg_budget_per_day', 0),
                    "recommended_days": city_info.get('recommended_days', 3)
                }
            else:
                # 尝试查找地区对应的城市
                region_cities = self._get_cities_by_region(city_name)
                if region_cities:
                    # 合并所有城市的景点信息
                    for actual_city in region_cities:
                        city_info = self.config_manager.get_city_info(actual_city)
                        if city_info:
                            result[actual_city] = {
                                "attractions": city_info.get('attractions', []),
                                "avg_budget_per_day": city_info.get('avg_budget_per_day', 0),
                                "recommended_days": city_info.get('recommended_days', 3),
                                "region": city_name  # 标记来源地区
                            }

        return {
            "success": True,
            "data": result,
            "cities_count": len(result)
        }

    def calculate_budget(self, city: str, days: int,
                        include_accommodation: bool = True,
                        include_transportation: bool = True) -> Dict[str, Any]:
        """
        计算旅游预算

        根据城市信息和旅行天数，计算各项费用预估。

        费用构成:
            - 门票: 景点门票总和
            - 餐饮: 日均预算的40% * 天数
            - 市内交通: 日均预算的20% * 天数
            - 住宿: 日均预算的30% * 天数 (可选)
            - 城际交通: 固定1000元 (可选)

        Args:
            city: str 目标城市名称
            days: int 旅行天数
            include_accommodation: bool 是否包含住宿费用，默认True
            include_transportation: bool 是否包含城际交通费用，默认True

        Returns:
            Dict[str, Any]: 预算结果
                - success: bool 是否成功
                - city: str 城市名称
                - budget: Dict[str, int] 各项费用明细
        """
        city_info = self.config_manager.get_city_info(city)
        if not city_info:
            return {
                "success": False,
                "error": f"未找到城市: {city}"
            }

        avg_daily = city_info.get('avg_budget_per_day', 400)
        attractions = city_info.get('attractions', [])

        # 计算各项费用
        ticket_total = sum(a.get('ticket', 0) for a in attractions)
        meal_cost = avg_daily * 0.4 * days
        local_transport = avg_daily * 0.2 * days

        budget = {
            "tickets": ticket_total,
            "meals": int(meal_cost),
            "local_transportation": int(local_transport)
        }

        if include_accommodation:
            accommodation = avg_daily * 0.3 * days
            budget['accommodation'] = int(accommodation)

        if include_transportation:
            inter_city_transport = 1000
            budget['inter_city_transportation'] = inter_city_transport

        budget['total'] = sum(budget.values())
        budget['days'] = days
        budget['avg_per_day'] = int(budget['total'] / days)

        return {
            "success": True,
            "city": city,
            "budget": budget
        }

    def get_city_info(self, city: str) -> Dict[str, Any]:
        """
        获取城市详细信息

        Args:
            city: str 城市名称

        Returns:
            Dict[str, Any]: 城市信息
                - success: bool 是否成功
                - city: str 城市名称
                - info: Dict 城市详细信息
        """
        city_info = self.config_manager.get_city_info(city)
        if city_info:
            return {
                "success": True,
                "city": city,
                "info": city_info
            }
        else:
            # 尝试查找地区对应的城市
            region_cities = self._get_cities_by_region(city)
            if region_cities:
                # 返回地区信息，包含所有城市
                first_city = region_cities[0]
                city_info = self.config_manager.get_city_info(first_city)
                if city_info:
                    # 使用地区名称，但包含实际城市信息
                    return {
                        "success": True,
                        "city": city,
                        "info": {
                            **city_info,
                            "name": city,
                            "is_region": True,
                            "cities": region_cities
                        }
                    }
            return {
                "success": False,
                "error": f"未找到城市: {city}"
            }

    def _get_cities_by_region(self, region: str) -> List[str]:
        """
        根据地区名称获取该地区的所有城市

        Args:
            region: str 地区名称，如"内蒙古"、"华北"

        Returns:
            List[str]: 该地区的城市名称列表
        """
        all_cities = self.config_manager.get_all_cities()
        region_cities = []
        for city_name in all_cities:
            city_info = self.config_manager.get_city_info(city_name)
            if city_info and city_info.get('region') == region:
                region_cities.append(city_name)
        return region_cities

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        执行工具调用

        统一的工具执行入口，通过工具名称调用对应的工具函数。

        Args:
            tool_name: str 工具名称，如"search_cities"
            **kwargs: 工具参数

        Returns:
            Dict[str, Any]: 工具执行结果
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"工具不存在: {tool_name}"
            }

        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": f"工具执行失败: {str(e)}"
            }
