# Project: Health & Performance Tracker

**Purpose:** To enable users to track nutritional intake and physical exertion, allowing nutritionists and fitness professionals to review data and provide professional feedback.

## 1. Batch Events

The system processes two main types of batch events received from user devices:

|Event Type|Description|
|---|---|
|**Meal Batch**|A collection of food intake data, including calories and specific macronutrient breakdowns.|
|**Exercise Batch**|A collection of physical activity data, including duration and heart rate metrics (min/avg/max).|

Export to Sheets

### Peak Load Guesstimate

- **Schedule:** Batches are typically sent at 10:00, 14:00, 18:00, and 22:00.
    
- **Peak Volume:** We expect the highest concurrency around **18:00** (post-work/pre-dinner).
    
- **Throughput:** Estimated **500 concurrent batches**, with each batch containing **1–10 individual items** (e.g., multiple food items in one meal or multiple heart rate segments in one workout).
    

## 2. Users

- **Customer:** The primary user (athlete or health-conscious individual) who records data via a mobile app or IoT device.
    
- **Review Team:** Professionals (Nutritionists and Fitness Coaches) who access the stored data via a dashboard to analyze trends and send feedback.
    

---

## 3. API Specification (OpenAPI)

### `POST /meals`

Uploads a batch of meal events for a specific user.

**Request Body (JSON):**

JSON
```JSON
{
  "user_id": "3e4567e1-b8bc-4d6a-8c08-4039a2b40000",
  "timestamp": "2026-01-14T18:00:00Z",
  "source_device": "iPhone 15 Pro",
  "items": [
    {
      "meal_id": "a1b2c3d4-e5f6-4a5b-b6c7-d8e9f0a1b2c3",
      "calories": 150,
      "meal_type": "Snack",
      "carbs_g": 20,
      "protein_g": 5,
      "fat_g": 2
    },
    {
      "meal_id": "b2c3d4e5-f6a7-5b6c-c7d8-e9f0a1b2c3d4",
      "calories": 750,
      "meal_type": "Dinner",
      "carbs_g": 60,
      "protein_g": 45,
      "fat_g": 25
    }
}
```

### `POST /exercises`

Uploads a batch of exercise heart rate metrics.

**Request Body (JSON):**

JSON

``` JSON
{
  "user_id": "3e4567e1-b8bc-4d6a-8c08-4039a2b40000",
  "timestamp": "2026-01-14T18:05:00Z",
  "source_device": "Garmin Forerunner 955",
  "items": [
    {
      "exercise_id": "c3d4e5f6-a7b8-6c7d-d8e9-f0a1b2c3d4e5",
      "type": "Running",
      "duration_min": 45,
      "avg_heart_rate": 145,
      "peak_heart_rate": 172
    }
  ]
}
```