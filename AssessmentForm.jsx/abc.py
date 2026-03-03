import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext.jsx';
import { useRiskCalculation } from '@/hooks/useRiskCalculation.js';
import pb from '@/lib/pocketbaseClient';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import DisclaimerConsent from '@/components/DisclaimerConsent.jsx';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const AssessmentForm = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { calculateRisks } = useRiskCalculation();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    personalInfo: { age: '', gender: '', height: '', weight: '', bmi: '' },
    familyHistory: { diabetes: false, heartDisease: false, cancer: false, hypertension: false, stroke: false, kidneyDisease: false, thyroid: false },
    lifestyleHabits: { smoking: '', alcohol: '', dietQuality: '', exerciseFrequency: '' },
    sleepAndStress: { sleepHours: 7, stressLevel: 5 },
    medicalConditions: [],
    symptoms: ''
  });

  const [errors, setErrors] = useState({});

  const totalSteps = 6;

  const updateFormData = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value }
    }));
    
    if (section === 'personalInfo' && (field === 'height' || field === 'weight')) {
      calculateBMI(
        field === 'height' ? value : formData.personalInfo.height,
        field === 'weight' ? value : formData.personalInfo.weight
      );
    }
  };

  const calculateBMI = (height, weight) => {
    if (height && weight) {
      const heightInMeters = parseFloat(height) / 100;
      const weightInKg = parseFloat(weight);
      const bmi = (weightInKg / (heightInMeters * heightInMeters)).toFixed(1);
      setFormData(prev => ({
        ...prev,
        personalInfo: { ...prev.personalInfo, bmi }
      }));
    }
  };

  const toggleMedicalCondition = (condition) => {
    setFormData(prev => ({
      ...prev,
      medicalConditions: prev.medicalConditions.includes(condition)
        ? prev.medicalConditions.filter(c => c !== condition)
        : [...prev.medicalConditions, condition]
    }));
  };

  const validateStep = (step) => {
    const newErrors = {};
    
    if (step === 1) {
      if (!formData.personalInfo.age) newErrors.age = 'Age is required';
      if (!formData.personalInfo.gender) newErrors.gender = 'Gender is required';
      if (!formData.personalInfo.height) newErrors.height = 'Height is required';
      if (!formData.personalInfo.weight) newErrors.weight = 'Weight is required';
    }
    
    if (step === 3) {
      if (!formData.lifestyleHabits.smoking) newErrors.smoking = 'Smoking status is required';
      if (!formData.lifestyleHabits.alcohol) newErrors.alcohol = 'Alcohol consumption is required';
      if (!formData.lifestyleHabits.dietQuality) newErrors.dietQuality = 'Diet quality is required';
      if (!formData.lifestyleHabits.exerciseFrequency) newErrors.exerciseFrequency = 'Exercise frequency is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!consent) {
      toast({
        title: 'Consent Required',
        description: 'Please read and accept the disclaimer to continue.',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      const risks = calculateRisks(formData);
      
      const riskScores = {
        diabetes: risks.diabetes.score,
        heartDisease: risks.heartDisease.score,
        hypertension: risks.hypertension.score,
        obesity: risks.obesity.score,
        stroke: risks.stroke.score
      };
      
      const contributingFactors = {
        diabetes: risks.diabetes.factors,
        heartDisease: risks.heartDisease.factors,
        hypertension: risks.hypertension.factors,
        obesity: risks.obesity.factors,
        stroke: risks.stroke.factors
      };

      const record = await pb.collection('assessments').create({
        userId: currentUser.id,
        personalInfo: formData.personalInfo,
        familyHistory: formData.familyHistory,
        lifestyleHabits: formData.lifestyleHabits,
        sleepAndStress: formData.sleepAndStress,
        medicalConditions: formData.medicalConditions,
        symptoms: formData.symptoms,
        riskScores,
        contributingFactors
      }, { $autoCancel: false });

      toast({
        title: 'Assessment Complete!',
        description: 'Your health risk assessment has been saved.'
      });

      navigate(`/results/${record.id}`);
    } catch (error) {
      console.error('Error saving assessment:', error);
      toast({
        title: 'Error',
        description: 'Failed to save assessment. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="age">Age *</Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.personalInfo.age}
                  onChange={(e) => updateFormData('personalInfo', 'age', e.target.value)}
                  placeholder="Enter your age"
                  className={errors.age ? 'border-red-500' : ''}
                />
                {errors.age && <p className="text-sm text-red-500 mt-1">{errors.age}</p>}
              </div>
              
              <div>
                <Label htmlFor="gender">Gender *</Label>
                <Select value={formData.personalInfo.gender} onValueChange={(value) => updateFormData('personalInfo', 'gender', value)}>
                  <SelectTrigger className={errors.gender ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                {errors.gender && <p className="text-sm text-red-500 mt-1">{errors.gender}</p>}
              </div>
              
              <div>
                <Label htmlFor="height">Height (cm) *</Label>
                <Input
                  id="height"
                  type="number"
                  value={formData.personalInfo.height}
                  onChange={(e) => updateFormData('personalInfo', 'height', e.target.value)}
                  placeholder="e.g., 170"
                  className={errors.height ? 'border-red-500' : ''}
                />
                {errors.height && <p className="text-sm text-red-500 mt-1">{errors.height}</p>}
              </div>
              
              <div>
                <Label htmlFor="weight">Weight (kg) *</Label>
                <Input
                  id="weight"
                  type="number"
                  value={formData.personalInfo.weight}
                  onChange={(e) => updateFormData('personalInfo', 'weight', e.target.value)}
                  placeholder="e.g., 70"
                  className={errors.weight ? 'border-red-500' : ''}
                />
                {errors.weight && <p className="text-sm text-red-500 mt-1">{errors.weight}</p>}
              </div>
            </div>
            
            {formData.personalInfo.bmi && (
              <div className="bg-primary/10 rounded-lg p-4 border border-primary/20">
                <p className="text-sm font-medium text-gray-700">Calculated BMI</p>
                <p className="text-3xl font-bold text-primary">{formData.personalInfo.bmi}</p>
                <p className="text-sm text-gray-600 mt-1">
                  {parseFloat(formData.personalInfo.bmi) < 18.5 && 'Underweight'}
                  {parseFloat(formData.personalInfo.bmi) >= 18.5 && parseFloat(formData.personalInfo.bmi) < 25 && 'Normal weight'}
                  {parseFloat(formData.personalInfo.bmi) >= 25 && parseFloat(formData.personalInfo.bmi) < 30 && 'Overweight'}
                  {parseFloat(formData.personalInfo.bmi) >= 30 && 'Obese'}
                </p>
              </div>
            )}
          </div>
        );
      
      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Family Medical History</h2>
            <p className="text-gray-600">Select any conditions that run in your immediate family (parents, siblings)</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.keys(formData.familyHistory).map(condition => (
                <div key={condition} className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-gray-50">
                  <Checkbox
                    id={condition}
                    checked={formData.familyHistory[condition]}
                    onCheckedChange={(checked) => updateFormData('familyHistory', condition, checked)}
                  />
                  <Label htmlFor={condition} className="cursor-pointer capitalize">
                    {condition.replace(/([A-Z])/g, ' $1').trim()}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Lifestyle Habits</h2>
            <div className="space-y-6">
              <div>
                <Label htmlFor="smoking">Smoking Status *</Label>
                <Select value={formData.lifestyleHabits.smoking} onValueChange={(value) => updateFormData('lifestyleHabits', 'smoking', value)}>
                  <SelectTrigger className={errors.smoking ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select smoking status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="never">Never smoked</SelectItem>
                    <SelectItem value="former">Former smoker</SelectItem>
                    <SelectItem value="current">Current smoker</SelectItem>
                  </SelectContent>
                </Select>
                {errors.smoking && <p className="text-sm text-red-500 mt-1">{errors.smoking}</p>}
              </div>
              
              <div>
                <Label htmlFor="alcohol">Alcohol Consumption *</Label>
                <Select value={formData.lifestyleHabits.alcohol} onValueChange={(value) => updateFormData('lifestyleHabits', 'alcohol', value)}>
                  <SelectTrigger className={errors.alcohol ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select alcohol consumption" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    <SelectItem value="light">Light (1-2 drinks/week)</SelectItem>
                    <SelectItem value="moderate">Moderate (3-7 drinks/week)</SelectItem>
                    <SelectItem value="heavy">Heavy (8+ drinks/week)</SelectItem>
                  </SelectContent>
                </Select>
                {errors.alcohol && <p className="text-sm text-red-500 mt-1">{errors.alcohol}</p>}
              </div>
              
              <div>
                <Label htmlFor="dietQuality">Diet Quality *</Label>
                <Select value={formData.lifestyleHabits.dietQuality} onValueChange={(value) => updateFormData('lifestyleHabits', 'dietQuality', value)}>
                  <SelectTrigger className={errors.dietQuality ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select diet quality" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="excellent">Excellent (mostly whole foods, balanced)</SelectItem>
                    <SelectItem value="good">Good (generally healthy)</SelectItem>
                    <SelectItem value="fair">Fair (some processed foods)</SelectItem>
                    <SelectItem value="poor">Poor (mostly processed/fast food)</SelectItem>
                  </SelectContent>
                </Select>
                {errors.dietQuality && <p className="text-sm text-red-500 mt-1">{errors.dietQuality}</p>}
              </div>
              
              <div>
                <Label htmlFor="exerciseFrequency">Exercise Frequency *</Label>
                <Select value={formData.lifestyleHabits.exerciseFrequency} onValueChange={(value) => updateFormData('lifestyleHabits', 'exerciseFrequency', value)}>
                  <SelectTrigger className={errors.exerciseFrequency ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select exercise frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily (5-7 days/week)</SelectItem>
                    <SelectItem value="regular">Regular (3-4 days/week)</SelectItem>
                    <SelectItem value="occasional">Occasional (1-2 days/week)</SelectItem>
                    <SelectItem value="never">Rarely/Never</SelectItem>
                  </SelectContent>
                </Select>
                {errors.exerciseFrequency && <p className="text-sm text-red-500 mt-1">{errors.exerciseFrequency}</p>}
              </div>
            </div>
          </div>
        );
      
      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Sleep & Stress</h2>
            <div className="space-y-8">
              <div>
                <Label>Average Sleep Hours per Night: {formData.sleepAndStress.sleepHours} hours</Label>
                <Slider
                  value={[formData.sleepAndStress.sleepHours]}
                  onValueChange={(value) => updateFormData('sleepAndStress', 'sleepHours', value[0])}
                  min={4}
                  max={12}
                  step={1}
                  className="mt-4"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>4 hours</span>
                  <span>12 hours</span>
                </div>
              </div>
              
              <div>
                <Label>Stress Level (1-10): {formData.sleepAndStress.stressLevel}</Label>
                <Slider
                  value={[formData.sleepAndStress.stressLevel]}
                  onValueChange={(value) => updateFormData('sleepAndStress', 'stressLevel', value[0])}
                  min={1}
                  max={10}
                  step={1}
                  className="mt-4"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>Low (1)</span>
                  <span>High (10)</span>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 5:
        const conditions = ['diabetes', 'hypertension', 'heartDisease', 'asthma', 'arthritis', 'depression', 'anxiety', 'thyroidDisorder'];
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Existing Medical Conditions</h2>
            <p className="text-gray-600">Select any conditions you currently have or have been diagnosed with</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {conditions.map(condition => (
                <div key={condition} className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-gray-50">
                  <Checkbox
                    id={`condition-${condition}`}
                    checked={formData.medicalConditions.includes(condition)}
                    onCheckedChange={() => toggleMedicalCondition(condition)}
                  />
                  <Label htmlFor={`condition-${condition}`} className="cursor-pointer capitalize">
                    {condition.replace(/([A-Z])/g, ' $1').trim()}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 6:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Current Symptoms</h2>
            <p className="text-gray-600">Describe any symptoms or health concerns you're currently experiencing (optional)</p>
            <Textarea
              value={formData.symptoms}
              onChange={(e) => setFormData(prev => ({ ...prev, symptoms: e.target.value }))}
              placeholder="e.g., frequent headaches, fatigue, chest pain, shortness of breath..."
              rows={6}
              className="resize-none"
            />
            
            <DisclaimerConsent consent={consent} onConsentChange={setConsent} />
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-3xl font-bold text-gray-900">Health Assessment</h1>
              <span className="text-sm font-medium text-gray-500">Step {currentStep} of {totalSteps}</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              />
            </div>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderStep()}
            </motion.div>
          </AnimatePresence>

          <div className="flex justify-between mt-8 pt-6 border-t">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            {currentStep < totalSteps ? (
              <Button onClick={handleNext} className="flex items-center gap-2">
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={loading || !consent} className="flex items-center gap-2">
                {loading ? 'Submitting...' : 'Complete Assessment'}
                <Check className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );


export default AssessmentForm;