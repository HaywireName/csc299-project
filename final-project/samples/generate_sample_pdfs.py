#!/usr/bin/env python3
"""
Script to generate sample PDFs for testing and demonstration purposes.
This script creates PDFs with various topics and sizes to test PKMS functionality.

Usage:
    python3 samples/generate_sample_pdfs.py

Note: This is a demo/testing script and is not part of the main PKMS application.
"""

from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  reportlab not installed. Install with: pip install reportlab")

def create_sample_pdfs():
    """Create sample PDFs for testing."""
    
    if not REPORTLAB_AVAILABLE:
        print("\n❌ Cannot create PDFs without reportlab library")
        print("Install with: pip install reportlab\n")
        return
    
    # Create samples directory if it doesn't exist
    samples_dir = Path(__file__).parent / 'pdfs'
    samples_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Creating sample PDFs in: {samples_dir}\n")
    
    # Create various sample PDFs with different topics and sizes
    samples = [
        ("The Art of Programming", create_programming_pdf, "Small (~400 words)"),
        ("Climate Change Overview", create_climate_pdf, "Small (~400 words)"),
        ("History of Computing", create_computing_history_pdf, "Medium (~800 words)"),
        ("Modern Web Development", create_web_dev_pdf, "Medium (~800 words)"),
        ("Artificial Intelligence Fundamentals", create_ai_fundamentals_pdf, "Large (~1500 words)"),
    ]
    
    for title, create_func, size_desc in samples:
        filename = title.replace(' ', '_') + '.pdf'
        filepath = samples_dir / filename
        print(f"📄 Creating: {filename} ({size_desc})...")
        create_func(filepath, title)
    
    print(f"\n✅ Sample PDFs created successfully!\n")
    print("📋 To add them to PKMS:")
    print("  1. Start PKMS: python3 main.py")
    print("  2. Navigate: pkms> documents")
    print(f"  3. Add PDF: documents> add {samples_dir}/The_Art_of_Programming.pdf")
    print("  4. Summarize: documents> summarize 1")
    print("  5. View: documents> view 1\n")

def create_programming_pdf(filepath, title):
    """Create a PDF about programming."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    content = """
    Programming is both an art and a science, requiring creativity, logical thinking, and attention to detail. 
    At its core, programming is about solving problems by breaking them down into smaller, manageable pieces 
    that a computer can execute. The choice of programming language depends on the task at hand, with each 
    language offering unique strengths and trade-offs.
    
    Good programming practices include writing clean, readable code that others can understand and maintain. 
    This involves using meaningful variable names, adding helpful comments, and following established coding 
    conventions. Testing is essential to ensure that code behaves as expected under various conditions.
    
    Modern development emphasizes collaboration and version control. Tools like Git enable teams to work 
    together effectively, tracking changes and managing different versions of code. Continuous integration 
    and deployment practices help catch bugs early and streamline the release process.
    
    The field of programming is constantly evolving, with new languages, frameworks, and paradigms emerging 
    regularly. Successful programmers embrace lifelong learning, staying curious about new technologies while 
    building a strong foundation in fundamental concepts that remain relevant across changing landscapes.
    """
    
    for paragraph in content.strip().split('\n\n'):
        story.append(Paragraph(paragraph.strip(), styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    doc.build(story)
    print(f"   ✓ Created: {filepath.name}")

def create_climate_pdf(filepath, title):
    """Create a PDF about climate change."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    content = """
    Climate change represents one of the most significant challenges facing humanity today. The scientific 
    consensus indicates that human activities, particularly the burning of fossil fuels, have led to increased 
    concentrations of greenhouse gases in the atmosphere. These gases trap heat, leading to rising global 
    temperatures and widespread environmental changes.
    
    The effects of climate change are already visible across the planet. Rising sea levels threaten coastal 
    communities, while extreme weather events become more frequent and severe. Changes in precipitation 
    patterns affect agriculture and water resources, and ecosystems struggle to adapt to rapidly changing 
    conditions.
    
    Addressing climate change requires coordinated action at multiple levels. International agreements like 
    the Paris Accord aim to limit global temperature increases through emissions reductions. Technological 
    innovations in renewable energy, energy efficiency, and carbon capture offer promising solutions.
    
    Individual actions also play a role in combating climate change. Choices about transportation, energy 
    use, diet, and consumption patterns collectively make a difference. Education and awareness are crucial 
    for building public support for climate policies and fostering a culture of sustainability.
    """
    
    for paragraph in content.strip().split('\n\n'):
        story.append(Paragraph(paragraph.strip(), styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    doc.build(story)
    print(f"   ✓ Created: {filepath.name}")

def create_computing_history_pdf(filepath, title):
    """Create a PDF about computing history."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    sections = [
        ("Early Mechanical Computers", """
        The history of computing begins with mechanical calculating devices dating back centuries. Charles 
        Babbage's Analytical Engine in the 1830s is often considered the first general-purpose computer 
        design, though it was never fully built. Ada Lovelace wrote what is recognized as the first computer 
        algorithm, envisioning the potential of computing beyond mere calculation.
        """),
        
        ("The Electronic Revolution", """
        The mid-20th century saw the development of electronic computers like ENIAC, which used vacuum tubes 
        to perform calculations thousands of times faster than mechanical devices. The invention of the 
        transistor revolutionized computing, enabling smaller, more reliable, and more powerful machines. 
        Integrated circuits further miniaturized components, leading to exponential increases in processing 
        power.
        """),
        
        ("Personal Computing Era", """
        The 1970s and 1980s brought computers into homes and offices with machines like the Apple II, IBM PC, 
        and Commodore 64. Graphical user interfaces made computers accessible to non-technical users. The 
        internet transformed computing from a tool for calculation into a platform for communication and 
        information sharing, fundamentally changing society and creating new industries and opportunities.
        """),
    ]
    
    for section_title, section_content in sections:
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(section_content.strip(), styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))
    
    doc.build(story)
    print(f"   ✓ Created: {filepath.name}")

def create_web_dev_pdf(filepath, title):
    """Create a PDF about web development."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    sections = [
        ("Frontend Technologies", """
        Modern web development relies on three core technologies: HTML for structure, CSS for styling, and 
        JavaScript for interactivity. Frontend frameworks like React, Vue, and Angular provide powerful tools 
        for building complex user interfaces. These frameworks enable component-based development, making 
        code more maintainable and reusable. Responsive design ensures websites work well on devices of all 
        sizes.
        """),
        
        ("Backend Systems", """
        The backend handles server-side logic, databases, and API endpoints. Popular backend frameworks 
        include Node.js, Django, Flask, and Ruby on Rails. RESTful APIs and GraphQL enable communication 
        between frontend and backend systems. Database management involves choosing between SQL databases 
        like PostgreSQL and NoSQL options like MongoDB based on application needs.
        """),
        
        ("Modern Development Practices", """
        Contemporary web development emphasizes automation and best practices. Build tools like Webpack and 
        Vite optimize code for production. Version control with Git enables team collaboration. Continuous 
        integration and deployment pipelines automate testing and deployment. Web performance optimization 
        ensures fast loading times and good user experience. Security considerations are paramount, including 
        protection against common vulnerabilities.
        """),
    ]
    
    for section_title, section_content in sections:
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(section_content.strip(), styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))
    
    doc.build(story)
    print(f"   ✓ Created: {filepath.name}")

def create_ai_fundamentals_pdf(filepath, title):
    """Create a larger PDF about AI fundamentals."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    sections = [
        ("What is Artificial Intelligence?", """
        Artificial Intelligence encompasses the development of computer systems that can perform tasks 
        typically requiring human intelligence. These tasks include visual perception, speech recognition, 
        decision-making, and language translation. AI systems learn from experience, adjust to new inputs, 
        and perform human-like tasks with varying degrees of autonomy and sophistication.
        
        The field of AI draws from multiple disciplines including computer science, mathematics, psychology, 
        linguistics, and neuroscience. Modern AI systems use algorithms that can identify patterns in data, 
        make predictions, and improve their performance over time through machine learning techniques.
        """),
        
        ("Machine Learning Approaches", """
        Machine learning is a subset of AI focused on building systems that learn from data. Supervised 
        learning uses labeled datasets to train models that can make predictions on new, unseen data. Common 
        applications include image classification, spam detection, and medical diagnosis. The model learns 
        by comparing its predictions to known correct answers and adjusting its parameters to minimize errors.
        
        Unsupervised learning discovers hidden patterns in unlabeled data without predefined categories. 
        Clustering algorithms group similar data points together, while dimensionality reduction techniques 
        simplify complex datasets while preserving important relationships. These approaches are valuable for 
        exploratory data analysis and feature discovery.
        
        Reinforcement learning trains agents to make sequences of decisions by rewarding desired behaviors. 
        The agent learns through trial and error, discovering strategies that maximize cumulative rewards. 
        This approach has achieved remarkable success in game playing, robotics, and autonomous systems, 
        including superhuman performance in chess, Go, and video games.
        """),
        
        ("Neural Networks and Deep Learning", """
        Neural networks are computing systems inspired by biological neural networks. They consist of 
        interconnected nodes organized in layers that process information and learn to recognize patterns. 
        Deep learning uses neural networks with many layers to learn hierarchical representations of data, 
        with each layer learning increasingly abstract features.
        
        Convolutional neural networks excel at processing grid-like data such as images. They use 
        specialized layers that detect local patterns like edges and textures in early layers, building up 
        to recognize complex objects in deeper layers. This architecture has revolutionized computer vision, 
        enabling applications from facial recognition to medical image analysis.
        
        Recurrent neural networks process sequential data by maintaining memory of previous inputs. This 
        makes them suitable for tasks involving time series, natural language, and speech. Advanced 
        architectures like LSTMs and transformers have enabled significant breakthroughs in machine 
        translation, text generation, and conversational AI.
        """),
        
        ("Applications and Impact", """
        AI applications span virtually every industry and domain. In healthcare, AI assists with disease 
        diagnosis, drug discovery, and personalized treatment planning. Computer vision systems analyze 
        medical images to detect cancers and other conditions, often matching or exceeding human expert 
        performance. Natural language processing enables medical chatbots and automated analysis of clinical 
        notes.
        
        Transportation is being transformed by autonomous vehicles that use AI to perceive their environment 
        and make driving decisions. Route optimization algorithms improve logistics and delivery services. 
        Traffic management systems use AI to reduce congestion and improve safety. These technologies promise 
        to reduce accidents, increase mobility, and transform urban planning.
        
        In business and finance, AI powers recommendation systems, fraud detection, and algorithmic trading. 
        Customer service chatbots handle routine inquiries, while sentiment analysis helps companies 
        understand public opinion. Credit scoring models and risk assessment tools make financial services 
        more efficient and accessible.
        """),
        
        ("Ethics and Future Directions", """
        The rapid advancement of AI raises important ethical considerations. Bias in training data can lead 
        to discriminatory AI systems, requiring careful attention to fairness and representation. Privacy 
        concerns arise from AI's ability to analyze personal data and make inferences about individuals. 
        Transparency and explainability are crucial for building trust and ensuring accountability.
        
        The future of AI involves continued progress in several key areas. More efficient algorithms and 
        specialized hardware will enable more powerful models. Research into general AI aims to create 
        systems with broader, more flexible intelligence. Human-AI collaboration will become increasingly 
        important, with AI augmenting rather than replacing human capabilities.
        
        Addressing AI's societal impact requires thoughtful governance and policy frameworks. Education and 
        workforce development will help people adapt to changing job markets. International cooperation on 
        AI safety and ethics can help ensure the technology benefits humanity broadly. The goal is to 
        harness AI's potential while mitigating risks and ensuring equitable access to its benefits.
        """),
    ]
    
    for section_title, section_content in sections:
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 0.15 * inch))
        for paragraph in section_content.strip().split('\n\n'):
            story.append(Paragraph(paragraph.strip(), styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
        story.append(Spacer(1, 0.25 * inch))
    
    doc.build(story)
    print(f"   ✓ Created: {filepath.name}")

if __name__ == "__main__":
    create_sample_pdfs()
