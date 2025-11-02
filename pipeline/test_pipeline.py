"""
Test Pipeline Stages
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.stages.stage1_data_ingestion import run_stage1
from pipeline.stages.stage2_feature_engineering import run_stage2

def test_stages():
    """Test pipeline stages 1 and 2"""
    print("="*70)
    print("WEEFARM ML PIPELINE - TESTING STAGES 1 & 2")
    print("="*70)
    
    try:
        # Test Stage 1: Data Ingestion
        print("\n🔄 Testing Stage 1: Data Ingestion...")
        data = run_stage1()
        
        # Verify data loaded
        assert len(data['equipment']) > 0, "No equipment data loaded"
        assert len(data['maintenance']) > 0, "No maintenance data loaded"
        assert len(data['failures']) > 0, "No failure data loaded"
        
        print("\n✅ Stage 1 Test PASSED!")
        print(f"   Equipment: {len(data['equipment'])} records")
        print(f"   Maintenance: {len(data['maintenance'])} records")
        print(f"   Failures: {len(data['failures'])} records")
        
        # Test Stage 2: Feature Engineering
        print("\n🔄 Testing Stage 2: Feature Engineering...")
        result = run_stage2(data)
        
        # Verify features calculated
        assert 'features' in result, "Features not generated"
        assert 'feature_columns' in result, "Feature columns not defined"
        assert len(result['features']) > 0, "No features calculated"
        
        print("\n✅ Stage 2 Test PASSED!")
        print(f"   Features calculated: {len(result['feature_columns'])}")
        print(f"   Equipment with features: {len(result['features'])}")
        
        # Show sample features
        print("\n📊 Sample Features (first 5 equipment):")
        print("="*70)
        sample = result['features'][['equipment_id'] + result['feature_columns'][:5]].head()
        print(sample.to_string())
        
        # Show feature statistics
        print("\n📊 Feature Statistics:")
        print("="*70)
        stats = result['features'][result['feature_columns']].describe()
        print(stats.to_string())
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎉 Stages 1 & 2 are working correctly!")
        print("   Ready to continue with Stages 3-6")
        
        return result
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_stages()
