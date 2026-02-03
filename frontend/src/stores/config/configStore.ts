import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ModelInfo } from '@/types';
import { apiService } from '@/services/api';
import { logger } from '@/utils/logger';

interface ConfigState {
  // API 配置
  apiBase: string;
  setApiBase: (base: string) => void;

  // 模型配置
  availableModels: ModelInfo[];
  currentModelId: string | null;
  loadingModels: boolean;
  loadModels: () => Promise<void>;
  setCurrentModelId: (modelId: string) => Promise<void>;
}

export const useConfigStore = create<ConfigState>()(
  devtools(
    persist(
      (set, get) => ({
        apiBase:
          typeof window !== 'undefined'
            ? window.ENV?.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
            : 'http://localhost:8000',

        availableModels: [],
        currentModelId: null,
        loadingModels: false,

        setApiBase: (apiBase) =>
          set({ apiBase }, false, 'config/setApiBase'),

        loadModels: async () => {
          set({ loadingModels: true }, false, 'config/loadModels/start');
          try {
            const data = await apiService.getAvailableModels();
            if (data.success && data.models.length > 0) {
              set(
                {
                  availableModels: data.models,
                  currentModelId: data.models[0].model_id,
                  loadingModels: false,
                },
                false,
                'config/loadModels/success'
              );
            }
          } catch (error) {
            // Set default models
            set(
              {
                availableModels: [
                  {
                    model_id: 'gpt-4o-mini',
                    name: 'OpenAI GPT-4o Mini',
                    provider: 'openai',
                    model: 'gpt-4o-mini',
                  },
                ],
                currentModelId: 'gpt-4o-mini',
                loadingModels: false,
              },
              false,
              'config/loadModels/fallback'
            );
          }
        },

        setCurrentModelId: async (modelId) => {
          const { currentModelId } = get();
          if (currentModelId === modelId) return;

          set({ currentModelId: modelId }, false, 'config/setCurrentModelId');

          const { currentSessionId } = await import('@/stores/session/sessionStore').then(
            (m) => m.useSessionStore.getState()
          );
          if (currentSessionId) {
            try {
              await apiService.setSessionModel(currentSessionId, modelId);
            } catch (error) {
              logger.error('设置会话模型失败:', error);
            }
          }
        },
      }),
      {
        name: 'config-storage',
        partialize: (state) => ({
          apiBase: state.apiBase,
          currentModelId: state.currentModelId,
        }),
      }
    ),
    { name: 'ConfigStore' }
  )
);
