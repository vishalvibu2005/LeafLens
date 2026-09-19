export interface BBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface TypePrediction {
  label: string | null;
  confidence: number | null;
  band: 'HIGH' | 'MEDIUM' | 'LOW' | null;
  top3: { label: string; confidence: number }[];
  is_demo: boolean;
}

export interface StagePrediction {
  label: string | null;
  confidence: number | null;
  band: 'HIGH' | 'MEDIUM' | 'LOW' | null;
  is_demo: boolean;
}

export interface HealthPrediction {
  label: string | null;
  confidence: number | null;
  band: 'HIGH' | 'MEDIUM' | 'LOW' | null;
  top3: { label: string; confidence: number }[];
  is_demo: boolean;
}

export interface ShapeFeatures {
  area: number;
  perimeter: number;
  width: number;
  height: number;
  aspect_ratio: number;
  circularity: number;
  solidity: number;
  extent: number;
  convex_hull_area: number;
  equivalent_diameter: number;
}

export interface ColorFeatures {
  rgb: { r: number; g: number; b: number };
  dominant_color: string | null;
}

export interface TextureFeatures {
  contrast: number;
  homogeneity: number;
  energy: number;
  correlation: number;
}

export interface LeafResult {
  leaf_id: number;
  detection_confidence: number;
  bbox: BBox;
  type: TypePrediction;
  health: HealthPrediction;
  growth_stage: StagePrediction;
  shape: ShapeFeatures;
  color: ColorFeatures;
  texture: TextureFeatures;
  views: { crop: string; mask: string; contours: string };
}

export interface Analysis {
  analysis_id: string;
  status: string;
  mode: 'production' | 'demo';
  created_at: string;
  thumbnail_url: string;
  leaf_count: number;
  leaf_results: LeafResult[];
  global_views: {
    original: string;
    preprocessed: string;
    detection: string;
    mask: string;
  };
}

export interface HealthStatus {
  status: string;
  models: {
    detector: boolean;
    detector_mode: string;
    leaf_classifier: boolean;
    health_classifier: boolean;
    stage_classifier: boolean;
  };
}

export interface DashboardStats {
  has_data: boolean;
  total_analyses?: number;
  leaves_detected?: number;
  most_analyzed_type?: string | null;
  average_confidence?: number | null;
  healthy_leaves?: number;
  affected_leaves?: number;
}

export interface ApiError {
  code: string;
  message: string;
}
