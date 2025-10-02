def pairs():
    boys = input("Имена мальчиков: ").split(",")
    girls = input("Имена девочек: ").split(",")
    
    boys = [b.strip() for b in boys]
    girls = [g.strip() for g in girls]

    if len(boys) != len(girls):
        print("Внимание, кто-то может остаться без пары")
        return

    boys_s = sorted(boys)
    girls_s = sorted(girls)

    print("Идеальные пары:")
    for b, g in zip(boys_s, girls_s):
        print(f"{b} и {g}")


pairs()
