# Google Slides Tool - Examples

Real-world examples demonstrating the Google Slides tool capabilities.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Business Use Cases](#business-use-cases)
3. [Educational Use Cases](#educational-use-cases)
4. [Marketing Use Cases](#marketing-use-cases)
5. [Advanced Examples](#advanced-examples)

---

## Basic Examples

### Example 1: Simple Title Slide

```python
from tools.communication.google_slides import GoogleSlides

tool = GoogleSlides(
    mode="create",
    title="Welcome Presentation",
    slides=[
        {
            "layout": "title",
            "title": "Welcome to Our Company",
            "subtitle": "New Employee Orientation 2024"
        }
    ]
)

result = tool.run()
print(f"Presentation URL: {result['result']['url']}")
```

**Output:**
```
Presentation URL: https://docs.google.com/presentation/d/1abc123def456/edit
```

### Example 2: Multi-Slide Presentation

```python
tool = GoogleSlides(
    mode="create",
    title="Product Overview",
    slides=[
        {
            "layout": "title",
            "title": "Product Overview",
            "subtitle": "Q4 2024"
        },
        {
            "layout": "section_header",
            "title": "Features"
        },
        {
            "layout": "title_and_body",
            "title": "Key Features",
            "content": "• Advanced analytics\n• Real-time collaboration\n• Cloud storage"
        },
        {
            "layout": "blank"
        }
    ],
    theme="modern"
)

result = tool.run()
```

---

## Business Use Cases

### Example 3: Quarterly Business Review

```python
tool = GoogleSlides(
    mode="create",
    title="Q4 2024 Business Review",
    slides=[
        {
            "layout": "title",
            "title": "Q4 2024 Business Review",
            "subtitle": "Executive Summary"
        },
        {
            "layout": "section_header",
            "title": "Financial Performance"
        },
        {
            "layout": "title_and_body",
            "title": "Revenue Overview",
            "content": "Total Revenue: $15.2M\nGrowth: +28% YoY\nProfit Margin: 32%",
            "image_url": "https://charts.company.com/revenue-q4.png",
            "notes": "Highlight the exceptional growth in enterprise segment"
        },
        {
            "layout": "two_columns",
            "title": "Performance Analysis",
            "left_content": "Strengths:\n• Strong enterprise sales\n• Product innovation\n• Customer retention 95%",
            "right_content": "Opportunities:\n• Market expansion APAC\n• New product lines\n• Strategic partnerships"
        },
        {
            "layout": "section_header",
            "title": "2025 Outlook"
        },
        {
            "layout": "title_and_body",
            "title": "Strategic Priorities",
            "content": "1. Launch AI-powered features\n2. Expand to 3 new markets\n3. Double sales team\n4. Achieve $25M ARR",
            "notes": "Emphasize the AI initiative as key differentiator"
        }
    ],
    theme="modern",
    share_with=["board@company.com", "executives@company.com"]
)

result = tool.run()
print(f"Shared with {len(result['result']['shared_with'])} recipients")
```

### Example 4: Sales Pitch Deck

```python
tool = GoogleSlides(
    mode="create",
    title="Enterprise Solution - Sales Pitch",
    slides=[
        {
            "layout": "title",
            "title": "Transform Your Business",
            "subtitle": "Enterprise Cloud Platform"
        },
        {
            "layout": "title_and_body",
            "title": "The Challenge",
            "content": "Companies struggle with:\n• Data silos\n• Manual processes\n• Poor collaboration\n• Security risks"
        },
        {
            "layout": "title_and_body",
            "title": "Our Solution",
            "content": "Unified platform that provides:\n• Centralized data management\n• Automated workflows\n• Real-time collaboration\n• Enterprise-grade security",
            "image_url": "https://assets.company.com/platform-diagram.png"
        },
        {
            "layout": "two_columns",
            "title": "Value Proposition",
            "left_content": "Before:\n• 40 hours/week manual work\n• 15% error rate\n• $200K annual costs",
            "right_content": "After:\n• 5 hours/week manual work\n• <1% error rate\n• $50K annual costs"
        },
        {
            "layout": "title_and_body",
            "title": "Client Success Stories",
            "content": "Fortune 500 clients:\n• 87% faster processing\n• 95% cost reduction\n• 4.9/5 satisfaction",
            "notes": "Have specific case studies ready if asked"
        },
        {
            "layout": "title_and_body",
            "title": "Next Steps",
            "content": "1. Schedule technical demo\n2. 30-day free trial\n3. Custom implementation plan\n4. Dedicated support team"
        }
    ],
    theme="colorful",
    share_with=["sales-team@company.com"]
)

result = tool.run()
```

### Example 5: Project Status Update

```python
tool = GoogleSlides(
    mode="create",
    title="Project Phoenix - Status Update",
    slides=[
        {
            "layout": "title",
            "title": "Project Phoenix",
            "subtitle": "Weekly Status Update - Week 12"
        },
        {
            "layout": "title_and_body",
            "title": "Milestones Completed",
            "content": "✓ Backend API development\n✓ Database migration\n✓ Security audit\n✓ Performance testing"
        },
        {
            "layout": "title_and_body",
            "title": "Current Sprint",
            "content": "In Progress:\n• Frontend UI components\n• Integration testing\n• Documentation\n\nBlocked:\n• Third-party API access (vendor delay)"
        },
        {
            "layout": "two_columns",
            "title": "Metrics",
            "left_content": "Progress:\n• Overall: 75% complete\n• On schedule\n• Under budget 5%",
            "right_content": "Quality:\n• Test coverage: 92%\n• Code review: 100%\n• Bugs: 3 critical (fixed)"
        },
        {
            "layout": "title_and_body",
            "title": "Next Week Goals",
            "content": "1. Complete frontend components\n2. Resolve API blocker\n3. Begin UAT preparation\n4. Update stakeholders",
            "notes": "Follow up with vendor on API access by Wed"
        }
    ],
    theme="simple",
    share_with=["project-team@company.com", "stakeholders@company.com"]
)

result = tool.run()
```

---

## Educational Use Cases

### Example 6: Course Lecture Slides

```python
tool = GoogleSlides(
    mode="create",
    title="Introduction to Machine Learning - Lecture 1",
    slides=[
        {
            "layout": "title",
            "title": "Introduction to Machine Learning",
            "subtitle": "CS 401 - Lecture 1"
        },
        {
            "layout": "title_and_body",
            "title": "Learning Objectives",
            "content": "By the end of this lecture, you will:\n• Understand ML fundamentals\n• Distinguish supervised vs unsupervised learning\n• Recognize common ML applications"
        },
        {
            "layout": "section_header",
            "title": "What is Machine Learning?"
        },
        {
            "layout": "title_and_body",
            "title": "Definition",
            "content": "Machine Learning is the study of algorithms that:\n• Learn from data\n• Make predictions\n• Improve with experience\n\nWithout being explicitly programmed"
        },
        {
            "layout": "two_columns",
            "title": "Types of Machine Learning",
            "left_content": "Supervised Learning:\n• Labeled data\n• Classification\n• Regression\n• Example: Email spam detection",
            "right_content": "Unsupervised Learning:\n• Unlabeled data\n• Clustering\n• Dimensionality reduction\n• Example: Customer segmentation"
        },
        {
            "layout": "title_and_body",
            "title": "Real-World Applications",
            "content": "• Recommendation systems (Netflix, Amazon)\n• Image recognition (Face ID)\n• Natural language processing (Siri, Alexa)\n• Autonomous vehicles\n• Medical diagnosis",
            "image_url": "https://edu.university.edu/ml-applications.png"
        },
        {
            "layout": "title_and_body",
            "title": "Next Lecture Preview",
            "content": "Topics:\n• Linear regression\n• Gradient descent\n• Hands-on exercise\n\nReading: Chapter 2, pages 45-78",
            "notes": "Remind students about lab session on Thursday"
        }
    ],
    theme="simple",
    share_with=["students@university.edu"]
)

result = tool.run()
```

### Example 7: Student Project Presentation

```python
tool = GoogleSlides(
    mode="create",
    title="Climate Change Analysis - Final Project",
    slides=[
        {
            "layout": "title",
            "title": "Climate Change Impact Analysis",
            "subtitle": "Environmental Science 301 - Team Delta"
        },
        {
            "layout": "title_and_body",
            "title": "Research Question",
            "content": "How has temperature change affected agricultural yields in the Midwest over the past 50 years?"
        },
        {
            "layout": "section_header",
            "title": "Methodology"
        },
        {
            "layout": "title_and_body",
            "title": "Data Collection",
            "content": "Sources:\n• NOAA climate database (1970-2020)\n• USDA agricultural reports\n• Regional weather stations\n\nSample size: 50 years, 12 states"
        },
        {
            "layout": "title_and_body",
            "title": "Key Findings",
            "content": "• Average temperature increase: 2.1°C\n• Crop yield decline: 15% (corn), 12% (wheat)\n• Drought frequency increased 3x\n• Growing season extended 2 weeks",
            "image_url": "https://research.edu/climate-charts.png"
        },
        {
            "layout": "title_and_body",
            "title": "Conclusions",
            "content": "1. Significant correlation between temperature and yield\n2. Adaptation strategies needed\n3. Economic impact: $4.2B annually\n4. Recommendations for sustainable farming"
        }
    ],
    theme="modern"
)

result = tool.run()
```

---

## Marketing Use Cases

### Example 8: Product Launch Campaign

```python
tool = GoogleSlides(
    mode="create",
    title="Product Launch Campaign - Widget Pro",
    slides=[
        {
            "layout": "title",
            "title": "Widget Pro Launch Campaign",
            "subtitle": "Q1 2025 Marketing Strategy"
        },
        {
            "layout": "title_and_body",
            "title": "Product Positioning",
            "content": "Widget Pro: The smartest widget for professionals\n\nTarget audience:\n• Business professionals\n• Age 30-50\n• Annual income $75K+\n• Tech-savvy"
        },
        {
            "layout": "section_header",
            "title": "Campaign Strategy"
        },
        {
            "layout": "two_columns",
            "title": "Channel Mix",
            "left_content": "Digital (60%):\n• Social media ads\n• Google search\n• Email campaigns\n• Influencer partnerships",
            "right_content": "Traditional (40%):\n• Print magazines\n• Trade shows\n• Direct mail\n• Radio spots"
        },
        {
            "layout": "title_and_body",
            "title": "Campaign Timeline",
            "content": "Pre-launch (2 weeks):\n• Teaser campaign\n• Influencer seeding\n\nLaunch week:\n• Press release\n• Social media blitz\n• Website takeover\n\nPost-launch (4 weeks):\n• Testimonials\n• Case studies\n• Retargeting",
            "image_url": "https://marketing.company.com/timeline.png"
        },
        {
            "layout": "title_and_body",
            "title": "Budget Allocation",
            "content": "Total budget: $500,000\n\n• Digital ads: $200K (40%)\n• Content creation: $100K (20%)\n• Events: $100K (20%)\n• PR/Media: $75K (15%)\n• Contingency: $25K (5%)"
        },
        {
            "layout": "title_and_body",
            "title": "Success Metrics",
            "content": "KPIs:\n• 100,000 website visits\n• 5,000 product registrations\n• 1,000 sales (first month)\n• 4.5+ star rating\n• $1M revenue (quarter)",
            "notes": "Weekly tracking dashboard to be set up"
        }
    ],
    theme="colorful",
    share_with=["marketing@company.com", "executives@company.com"]
)

result = tool.run()
```

---

## Advanced Examples

### Example 9: Modifying Existing Presentation

```python
# First, get the presentation_id from a previous creation
# presentation_id = "1abc123def456"

tool = GoogleSlides(
    mode="modify",
    presentation_id="1abc123def456",
    slides=[
        {
            "layout": "section_header",
            "title": "Appendix"
        },
        {
            "layout": "title_and_body",
            "title": "Additional Resources",
            "content": "Documentation: https://docs.company.com\nSupport: support@company.com\nCommunity: forum.company.com"
        },
        {
            "layout": "title_and_body",
            "title": "Contact Information",
            "content": "Sales: 1-800-WIDGETS\nEmail: sales@company.com\nSchedule demo: company.com/demo"
        }
    ]
)

result = tool.run()
print(f"Added {result['result']['slides_added']} new slides")
```

### Example 10: Comprehensive Report with All Layout Types

```python
tool = GoogleSlides(
    mode="create",
    title="2024 Annual Report - Complete",
    slides=[
        # Cover
        {
            "layout": "title",
            "title": "2024 Annual Report",
            "subtitle": "Building Tomorrow, Today"
        },

        # Executive Summary Section
        {
            "layout": "section_header",
            "title": "Executive Summary"
        },
        {
            "layout": "title_and_body",
            "title": "Year in Review",
            "content": "2024 was a year of transformation:\n• Revenue: $50M (+35%)\n• Customers: 10,000 (+50%)\n• Employees: 250 (+40%)\n• Markets: 15 countries (+5)",
            "notes": "CEO to present this section"
        },

        # Financial Performance Section
        {
            "layout": "section_header",
            "title": "Financial Performance"
        },
        {
            "layout": "title_and_body",
            "title": "Revenue Growth",
            "content": "Quarterly breakdown:\nQ1: $10M\nQ2: $12M\nQ3: $13M\nQ4: $15M\n\nTotal: $50M",
            "image_url": "https://reports.company.com/revenue-chart.png"
        },
        {
            "layout": "two_columns",
            "title": "Financial Highlights",
            "left_content": "Revenue streams:\n• Enterprise: $30M (60%)\n• SMB: $15M (30%)\n• Individual: $5M (10%)",
            "right_content": "Expenses:\n• R&D: $15M (30%)\n• Sales: $12.5M (25%)\n• Operations: $10M (20%)\n• Other: $12.5M (25%)"
        },

        # Product Innovation Section
        {
            "layout": "section_header",
            "title": "Product Innovation"
        },
        {
            "layout": "title_and_body",
            "title": "New Products Launched",
            "content": "2024 Product launches:\n• Widget Pro (February)\n• Widget Enterprise (June)\n• Widget AI (November)\n\nTotal: 3 major releases, 24 feature updates"
        },

        # Customer Success Section
        {
            "layout": "section_header",
            "title": "Customer Success"
        },
        {
            "layout": "title_and_body",
            "title": "Customer Metrics",
            "content": "Satisfaction scores:\n• NPS: 72 (Industry avg: 45)\n• CSAT: 4.8/5.0\n• Retention: 95%\n• Referrals: 40%",
            "image_url": "https://reports.company.com/customer-metrics.png"
        },
        {
            "layout": "two_columns",
            "title": "Customer Testimonials",
            "left_content": '"Widget transformed our workflow. We save 20 hours/week!"\n- Fortune 500 CIO',
            "right_content": '"Best investment we made this year. ROI in 3 months."\n- Small Business Owner'
        },

        # Team & Culture Section
        {
            "layout": "section_header",
            "title": "Team & Culture"
        },
        {
            "layout": "title_and_body",
            "title": "Growing Our Team",
            "content": "Team expansion:\n• Engineering: 100 (+45%)\n• Sales: 75 (+50%)\n• Support: 50 (+35%)\n• Operations: 25 (+30%)\n\nEmployee satisfaction: 4.6/5.0"
        },

        # Looking Forward Section
        {
            "layout": "section_header",
            "title": "2025 Outlook"
        },
        {
            "layout": "title_and_body",
            "title": "Strategic Priorities",
            "content": "Focus areas for 2025:\n1. AI integration across products\n2. Global expansion (APAC focus)\n3. Enterprise partnerships\n4. Sustainability initiatives\n5. Team development",
            "notes": "Board discussion on AI strategy next month"
        },

        # Closing
        {
            "layout": "title_and_body",
            "title": "Thank You",
            "content": "To our customers, partners, and team:\n\nThank you for an incredible 2024.\n\nHere's to an even better 2025!"
        },

        # Appendix
        {
            "layout": "blank"
        }
    ],
    theme="modern",
    share_with=["board@company.com", "investors@company.com", "all-staff@company.com"]
)

result = tool.run()
print(f"Created {result['result']['slide_count']} slides")
print(f"Shared with {len(result['result']['shared_with'])} groups")
print(f"View at: {result['result']['url']}")
```

---

## Best Practices

### 1. Content Guidelines

- Keep text concise (max 6 bullet points per slide)
- Use high-contrast colors for readability
- Include speaker notes for complex slides
- Add images to break up text-heavy sections

### 2. Layout Selection

- **title**: Use for cover slides and section breaks
- **title_and_body**: Best for lists and key points
- **two_columns**: Great for comparisons and pros/cons
- **section_header**: Use to divide major sections
- **blank**: For custom content or full images

### 3. Theme Selection

- **default**: Professional, neutral
- **simple**: Clean, minimal distraction
- **modern**: Contemporary, tech-forward
- **colorful**: Engaging, creative presentations

### 4. Sharing Strategy

- Only share with necessary recipients
- Use group emails for team distribution
- Consider view-only vs. edit permissions
- Include a cover email with context

---

## Error Handling

```python
from tools.communication.google_slides import GoogleSlides

try:
    tool = GoogleSlides(
        mode="create",
        title="Test Presentation",
        slides=[
            {
                "layout": "title_and_body",
                "title": "Test Slide",
                "content": "Content here"
            }
        ]
    )
    result = tool.run()

    if result["success"]:
        print(f"Success! URL: {result['result']['url']}")
    else:
        print(f"Error: {result['error']['message']}")

except Exception as e:
    print(f"Exception occurred: {e}")
```

---

## Integration with Other Tools

### Example: Generate presentation from data analysis

```python
# 1. Analyze data with another tool
data_analysis_result = analyze_sales_data()

# 2. Create presentation with insights
tool = GoogleSlides(
    mode="create",
    title="Sales Analysis Results",
    slides=[
        {
            "layout": "title",
            "title": "Sales Analysis",
            "subtitle": f"Generated {data_analysis_result['date']}"
        },
        {
            "layout": "title_and_body",
            "title": "Key Insights",
            "content": data_analysis_result['summary']
        },
        {
            "layout": "title_and_body",
            "title": "Recommendations",
            "content": data_analysis_result['recommendations'],
            "image_url": data_analysis_result['chart_url']
        }
    ],
    theme="modern",
    share_with=["analytics-team@company.com"]
)

result = tool.run()
```

---

## Additional Resources

- [Google Slides API Documentation](https://developers.google.com/slides)
- [Presentation Design Best Practices](https://www.google.com/slides/about/)
- [Tool Repository](https://github.com/your-org/agentswarm-tools)

---

**Note**: All examples use mock mode by default. Set `USE_MOCK_APIS=false` and configure `GOOGLE_SLIDES_CREDENTIALS` for production use.
