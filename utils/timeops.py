from datetime import datetime, timedelta


def main():
    today = datetime.now().date()
    svo_start = datetime(day=24, month=2, year=2022).date()
    donbass_war_start = svo_start - timedelta(days=2846)
    
    days_svo = (today - svo_start).days
    days_donbass_war = (today - donbass_war_start).days

    return {
        "svo": days_svo,
        "donbass": days_donbass_war,
    }


if __name__ == "__main__":
    main()