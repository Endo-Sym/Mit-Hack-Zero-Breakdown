class ROICalculationTool:
    @staticmethod
    def get_tool_spec():
        return {
            "toolSpec": {
                "name": "ROI_Calculation_Tool",
                "description": "Calculates the ROI based on the time left before breakdown.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "plant_size": {"type": "string", "description": "Plant size (Small, Medium, Large)"},
                            "factory_count": {"type": "integer", "description": "Number of factories"},
                            "loss_value_per_4hrs": {"type": "number", "description": "Financial loss per 4 hours per factory (in million THB)"},
                            "production_per_day": {"type": "number", "description": "Production per day (tons)"},
                        },
                        "required": ["plant_size", "factory_count", "loss_value_per_4hrs", "production_per_day"]
                    }
                }
            }
        }
    @staticmethod
    def calculate_roi(request: ROIRequest):
    """คำนวณ ROI ของการซ่อมบำรุงในช่วงเวลาต่างๆ"""
    try:
        # Calculate efficiency loss
        efficiency_current = request.current_health_percentage / 100
        efficiency_comparison = request.comparison_health_percentage / 100

        # Estimate days until breakdown
        days_until_breakdown_current = (100 - request.current_health_percentage) * 2
        days_until_breakdown_comparison = (100 - request.comparison_health_percentage) * 2

        # Production loss
        production_loss_current = request.daily_production_value * (1 - efficiency_current) * days_until_breakdown_current
        production_loss_comparison = request.daily_production_value * (1 - efficiency_comparison) * days_until_breakdown_comparison

        # ROI calculation
        savings = production_loss_comparison - production_loss_current
        roi_percentage = ((savings - request.repair_cost) / request.repair_cost) * 100 if request.repair_cost > 0 else 0

        prompt = f"""วิเคราะห์ ROI ของการซ่อมบำรุงเครื่องจักร:

        สถานการณ์ปัจจุบัน:
        - สุขภาพเครื่องจักร: {request.current_health_percentage}%
        - ประมาณการวันก่อนเสียหาย: {days_until_breakdown_current:.0f} วัน
        - การสูญเสียจากประสิทธิภาพลดลง: {production_loss_current:,.2f} บาท

        สถานการณ์เปรียบเทียบ (ถ้าซ่อมที่ {request.comparison_health_percentage}%):
        - ประมาณการวันก่อนเสียหาย: {days_until_breakdown_comparison:.0f} วัน
        - การสูญเสียจากประสิทธิภาพลดลง: {production_loss_comparison:,.2f} บาท

        ค่าใช้จ่ายในการซ่อม: {request.repair_cost:,.2f} บาท
        ผลตอบแทนจากการลงทุน (ROI): {roi_percentage:.2f}%

        กรุณาอธิบายผลการวิเคราะห์และให้คำแนะนำว่าควรซ่อมตอนไหนดีที่สุด"""
        
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024
        })

        # ส่งคำขอไปยังโมเดล qwen.qwen3-32b-v1:0 ผ่าน API
        response_body = client.converse(
            modelId="qwen.qwen3-32b-v1:0",
            body=body
        )
        analysis= response_body['output']['message']['content'][0]['text']

        return {
            "current_scenario": {
                "health_percentage": request.current_health_percentage,
                "days_until_breakdown": round(days_until_breakdown_current, 1),
                "production_loss": round(production_loss_current, 2)
            },
            "comparison_scenario": {
                "health_percentage": request.comparison_health_percentage,
                "days_until_breakdown": round(days_until_breakdown_comparison, 1),
                "production_loss": round(production_loss_comparison, 2)
            },
            "repair_cost": request.repair_cost,
            "savings": round(savings, 2),
            "roi_percentage": round(roi_percentage, 2),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
