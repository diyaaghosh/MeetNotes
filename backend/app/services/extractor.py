def convert_to_bullets(summary):
   
    bullets = []

    for s in summary:
        s = s.strip()
        if s:
            bullets.append("• " + s)

    return bullets