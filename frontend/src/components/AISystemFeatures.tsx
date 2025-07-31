import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRobot, faSearch, faChartBar } from '@fortawesome/free-solid-svg-icons';

interface Feature {
  icon: any;
  iconType: 'emoji' | 'geometric' | 'text' | 'fontawesome';
  title: string;
  description: string;
  color: string;
}

const features: Feature[] = [
  {
    icon: faRobot,
    iconType: 'fontawesome',
    title: 'Expert AI Analysis',
    description: 'Our VehicleComparisonAgent acts as an expert car reviewer, analyzing technical specifications, reliability data, and professional reviews to create comprehensive comparisons.',
    color: 'bg-blue-50 text-blue-600'
  },
  {
    icon: faSearch,
    iconType: 'fontawesome',
    title: 'Live Market Intelligence',
    description: 'Our SriLankanAdFinderAgent searches real-time listings from ikman.lk and riyasewana.com, finding the most current market prices and availability.',
    color: 'bg-green-50 text-green-600'
  },
  {
    icon: faChartBar,
    iconType: 'fontawesome',
    title: 'Detailed Data Extraction',
    description: 'Our AdDetailsExtractorAgent uses advanced web scraping to extract precise details like pricing, mileage, location, and vehicle condition from each listing.',
    color: 'bg-purple-50 text-purple-600'
  }
];

// Icon Components
const EmojiIcon = ({ icon }: { icon: string }) => (
  <div className="text-3xl mb-6">
    {icon}
  </div>
);

const GeometricIcon = ({ type, color }: { type: string; color: string }) => {
  const getGeometricIcon = () => {
    switch (type) {
      case 'robot':
        return (
          <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-6`}>
            <div className="w-6 h-6 border-2 border-current rounded-sm">
              <div className="flex justify-between mt-1 px-1">
                <div className="w-1 h-1 bg-current rounded-full"></div>
                <div className="w-1 h-1 bg-current rounded-full"></div>
              </div>
              <div className="w-3 h-1 bg-current rounded mx-auto mt-1"></div>
            </div>
          </div>
        );
      case 'search':
        return (
          <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-6`}>
            <div className="relative">
              <div className="w-4 h-4 border-2 border-current rounded-full"></div>
              <div className="absolute top-3 left-3 w-2 h-0.5 bg-current transform rotate-45"></div>
            </div>
          </div>
        );
      case 'chart':
        return (
          <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-6`}>
            <div className="flex items-end space-x-1">
              <div className="w-1 h-6 bg-current rounded-sm"></div>
              <div className="w-1 h-4 bg-current rounded-sm"></div>
              <div className="w-1 h-5 bg-current rounded-sm"></div>
              <div className="w-1 h-3 bg-current rounded-sm"></div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };
  return getGeometricIcon();
};

const TextIcon = ({ text, color }: { text: string; color: string }) => (
  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${color} mb-6`}>
    <span className="text-lg font-bold">{text}</span>
  </div>
);

const FeatureCard = ({ icon, iconType, title, description, color }: Feature) => {
  const renderIcon = () => {
    switch (iconType) {
      case 'emoji':
        return <EmojiIcon icon={icon} />;
      case 'geometric':
        return <GeometricIcon type={icon} color={color} />;
      case 'text':
        return <TextIcon text={icon} color={color} />;
      case 'fontawesome':
        return (
          <div className="mb-6">
            <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${color}`}>
              <FontAwesomeIcon icon={icon} className="text-base" style={{fontSize: '1.25rem'}} />
            </div>
          </div>
        );
      default:
        return <EmojiIcon icon={icon} />;
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300">
      {renderIcon()}
      <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
};

const TechnologyBadges = () => {
  const technologies = [
    'CrewAI Multi-Agent System',
    'OpenAI GPT-4',
    'Real-time Web Scraping',
    'Sri Lankan Market Focus'
  ];

  return (
    <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
      {technologies.map((tech) => (
        <span key={tech} className="bg-white/80 px-4 py-2 rounded-full">
          {tech}
        </span>
      ))}
    </div>
  );
};

export default function AISystemFeatures() {
  return (
    <div className="max-w-6xl mx-auto px-4 mt-16">
      {/* Header Section */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          How Our AI System Works
        </h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Our multi-agent AI system combines expert analysis with real-time market data to give you comprehensive vehicle insights.
        </p>
      </div>
      
      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8">
        {features.map((feature) => (
          <FeatureCard
            key={feature.title}
            icon={feature.icon}
            iconType={feature.iconType}
            title={feature.title}
            description={feature.description}
            color={feature.color}
          />
        ))}
      </div>
      
      {/* Technology Section */}
      <div className="mt-16 text-center">
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Powered by Advanced AI Technology
          </h3>
          <TechnologyBadges />
        </div>
      </div>
    </div>
  );
}
