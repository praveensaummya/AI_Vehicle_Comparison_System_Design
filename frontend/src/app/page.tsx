import VehicleComparisonForm from '@/components/VehicleComparisonForm';
import AISystemFeatures from '@/components/AISystemFeatures';
import '@/lib/fontawesome';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="py-12">
        <VehicleComparisonForm />
        <AISystemFeatures />
      </div>
    </main>
  );
}
