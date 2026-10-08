from profile_loader import load_profile


profile = load_profile()

print("Name:", profile["name"])
print("Target Roles:", profile["target_roles"])
print("Experience:", profile["experience_years"], "years")
print("Current Role:", profile["current_role"])
print("Skills:", ", ".join(profile["skills"]))