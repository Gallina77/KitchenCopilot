"""
HTML component templates for the KitchenCopilot homepage
"""

def hero_section():
    """Returns the hero section HTML"""
    return """
        <div class='hero-section'>
            <h1>
                <span class='hero-title'>
                    🍽️ KitchenCopilot
                </span>
            </h1>
            <p>Machine learning-powered meal demand forecasting for cafeterias</p>
        </div>
    """

def journey_step(number, title, description):
    """Returns a single journey step HTML"""
    return f"""
        <div class='journey-step'>
            <div class='step-circle'>{number}</div>
            <h4>{title}</h4>
            <p class='step-description'>{description}</p>
        </div>
    """

def feature_card(icon, title, description):
    """Returns a feature card HTML"""
    return f"""
        <div class='feature-container'>
            <h3><i class="bi {icon}"></i> {title}</h3>
            <p class='feature-description'>{description}</p>
        </div>
    """

def roadmap_card(badge_text, badge_variant, icon, title, description):
    """Returns a roadmap card HTML
    
    Args:
        badge_text: Text to display in the badge
        badge_variant: CSS class variant ('primary', 'success', 'warning', 'info')
        icon: Bootstrap icon class name
        title: Card title
        description: Card description
    """
    return f"""
        <div class='roadmap-card'>
            <span class='roadmap-badge roadmap-badge-{badge_variant}'>{badge_text}</span>
            <h3><i class="bi {icon}"></i> {title}</h3>
            <p class='roadmap-description'>{description}</p>
        </div>
    """

def footer_section():
    """Returns the footer HTML"""
    return """
        <div class='footer'>
            <div class='footer-grid'>
                <div>
                    <h4>KitchenCopilot v1.0</h4>
                    <p>Last Updated: January, 2026</p>
                </div>
                <div>
                    <h4>References</h4>
                    <p><a href="https://github.com/Gallina77/KitchenCopilot.git" target="_blank">GitHub Repository</a></p>
                    <p><a href="https://open-meteo.com" target="_blank">Weather API</a></p>
                </div>
                <div>
                    <h4>Support</h4>
                    <a href="mailto:sandra.grassl77@gmail.com">Contact me</a>
                </div>
            </div>
        </div>
    """