export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  auth: {
    Tables: {
      audit_log_entries: {
        Row: {
          created_at: string | null
          id: string
          instance_id: string | null
          ip_address: string
          payload: Json | null
        }
        Insert: {
          created_at?: string | null
          id: string
          instance_id?: string | null
          ip_address?: string
          payload?: Json | null
        }
        Update: {
          created_at?: string | null
          id?: string
          instance_id?: string | null
          ip_address?: string
          payload?: Json | null
        }
        Relationships: []
      }
      flow_state: {
        Row: {
          auth_code: string
          auth_code_issued_at: string | null
          authentication_method: string
          code_challenge: string
          code_challenge_method: Database["auth"]["Enums"]["code_challenge_method"]
          created_at: string | null
          id: string
          provider_access_token: string | null
          provider_refresh_token: string | null
          provider_type: string
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          auth_code: string
          auth_code_issued_at?: string | null
          authentication_method: string
          code_challenge: string
          code_challenge_method: Database["auth"]["Enums"]["code_challenge_method"]
          created_at?: string | null
          id: string
          provider_access_token?: string | null
          provider_refresh_token?: string | null
          provider_type: string
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          auth_code?: string
          auth_code_issued_at?: string | null
          authentication_method?: string
          code_challenge?: string
          code_challenge_method?: Database["auth"]["Enums"]["code_challenge_method"]
          created_at?: string | null
          id?: string
          provider_access_token?: string | null
          provider_refresh_token?: string | null
          provider_type?: string
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: []
      }
      identities: {
        Row: {
          created_at: string | null
          email: string | null
          id: string
          identity_data: Json
          last_sign_in_at: string | null
          provider: string
          provider_id: string
          updated_at: string | null
          user_id: string
        }
        Insert: {
          created_at?: string | null
          email?: string | null
          id?: string
          identity_data: Json
          last_sign_in_at?: string | null
          provider: string
          provider_id: string
          updated_at?: string | null
          user_id: string
        }
        Update: {
          created_at?: string | null
          email?: string | null
          id?: string
          identity_data?: Json
          last_sign_in_at?: string | null
          provider?: string
          provider_id?: string
          updated_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "identities_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      instances: {
        Row: {
          created_at: string | null
          id: string
          raw_base_config: string | null
          updated_at: string | null
          uuid: string | null
        }
        Insert: {
          created_at?: string | null
          id: string
          raw_base_config?: string | null
          updated_at?: string | null
          uuid?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          raw_base_config?: string | null
          updated_at?: string | null
          uuid?: string | null
        }
        Relationships: []
      }
      mfa_amr_claims: {
        Row: {
          authentication_method: string
          created_at: string
          id: string
          session_id: string
          updated_at: string
        }
        Insert: {
          authentication_method: string
          created_at: string
          id: string
          session_id: string
          updated_at: string
        }
        Update: {
          authentication_method?: string
          created_at?: string
          id?: string
          session_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "mfa_amr_claims_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      mfa_challenges: {
        Row: {
          created_at: string
          factor_id: string
          id: string
          ip_address: unknown
          otp_code: string | null
          verified_at: string | null
          web_authn_session_data: Json | null
        }
        Insert: {
          created_at: string
          factor_id: string
          id: string
          ip_address: unknown
          otp_code?: string | null
          verified_at?: string | null
          web_authn_session_data?: Json | null
        }
        Update: {
          created_at?: string
          factor_id?: string
          id?: string
          ip_address?: unknown
          otp_code?: string | null
          verified_at?: string | null
          web_authn_session_data?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "mfa_challenges_auth_factor_id_fkey"
            columns: ["factor_id"]
            isOneToOne: false
            referencedRelation: "mfa_factors"
            referencedColumns: ["id"]
          },
        ]
      }
      mfa_factors: {
        Row: {
          created_at: string
          factor_type: Database["auth"]["Enums"]["factor_type"]
          friendly_name: string | null
          id: string
          last_challenged_at: string | null
          phone: string | null
          secret: string | null
          status: Database["auth"]["Enums"]["factor_status"]
          updated_at: string
          user_id: string
          web_authn_aaguid: string | null
          web_authn_credential: Json | null
        }
        Insert: {
          created_at: string
          factor_type: Database["auth"]["Enums"]["factor_type"]
          friendly_name?: string | null
          id: string
          last_challenged_at?: string | null
          phone?: string | null
          secret?: string | null
          status: Database["auth"]["Enums"]["factor_status"]
          updated_at: string
          user_id: string
          web_authn_aaguid?: string | null
          web_authn_credential?: Json | null
        }
        Update: {
          created_at?: string
          factor_type?: Database["auth"]["Enums"]["factor_type"]
          friendly_name?: string | null
          id?: string
          last_challenged_at?: string | null
          phone?: string | null
          secret?: string | null
          status?: Database["auth"]["Enums"]["factor_status"]
          updated_at?: string
          user_id?: string
          web_authn_aaguid?: string | null
          web_authn_credential?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "mfa_factors_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      one_time_tokens: {
        Row: {
          created_at: string
          id: string
          relates_to: string
          token_hash: string
          token_type: Database["auth"]["Enums"]["one_time_token_type"]
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id: string
          relates_to: string
          token_hash: string
          token_type: Database["auth"]["Enums"]["one_time_token_type"]
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          relates_to?: string
          token_hash?: string
          token_type?: Database["auth"]["Enums"]["one_time_token_type"]
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "one_time_tokens_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      refresh_tokens: {
        Row: {
          created_at: string | null
          id: number
          instance_id: string | null
          parent: string | null
          revoked: boolean | null
          session_id: string | null
          token: string | null
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          id?: number
          instance_id?: string | null
          parent?: string | null
          revoked?: boolean | null
          session_id?: string | null
          token?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          id?: number
          instance_id?: string | null
          parent?: string | null
          revoked?: boolean | null
          session_id?: string | null
          token?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "refresh_tokens_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      saml_providers: {
        Row: {
          attribute_mapping: Json | null
          created_at: string | null
          entity_id: string
          id: string
          metadata_url: string | null
          metadata_xml: string
          name_id_format: string | null
          sso_provider_id: string
          updated_at: string | null
        }
        Insert: {
          attribute_mapping?: Json | null
          created_at?: string | null
          entity_id: string
          id: string
          metadata_url?: string | null
          metadata_xml: string
          name_id_format?: string | null
          sso_provider_id: string
          updated_at?: string | null
        }
        Update: {
          attribute_mapping?: Json | null
          created_at?: string | null
          entity_id?: string
          id?: string
          metadata_url?: string | null
          metadata_xml?: string
          name_id_format?: string | null
          sso_provider_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "saml_providers_sso_provider_id_fkey"
            columns: ["sso_provider_id"]
            isOneToOne: false
            referencedRelation: "sso_providers"
            referencedColumns: ["id"]
          },
        ]
      }
      saml_relay_states: {
        Row: {
          created_at: string | null
          flow_state_id: string | null
          for_email: string | null
          id: string
          redirect_to: string | null
          request_id: string
          sso_provider_id: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          flow_state_id?: string | null
          for_email?: string | null
          id: string
          redirect_to?: string | null
          request_id: string
          sso_provider_id: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          flow_state_id?: string | null
          for_email?: string | null
          id?: string
          redirect_to?: string | null
          request_id?: string
          sso_provider_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "saml_relay_states_flow_state_id_fkey"
            columns: ["flow_state_id"]
            isOneToOne: false
            referencedRelation: "flow_state"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "saml_relay_states_sso_provider_id_fkey"
            columns: ["sso_provider_id"]
            isOneToOne: false
            referencedRelation: "sso_providers"
            referencedColumns: ["id"]
          },
        ]
      }
      schema_migrations: {
        Row: {
          version: string
        }
        Insert: {
          version: string
        }
        Update: {
          version?: string
        }
        Relationships: []
      }
      sessions: {
        Row: {
          aal: Database["auth"]["Enums"]["aal_level"] | null
          created_at: string | null
          factor_id: string | null
          id: string
          ip: unknown | null
          not_after: string | null
          refreshed_at: string | null
          tag: string | null
          updated_at: string | null
          user_agent: string | null
          user_id: string
        }
        Insert: {
          aal?: Database["auth"]["Enums"]["aal_level"] | null
          created_at?: string | null
          factor_id?: string | null
          id: string
          ip?: unknown | null
          not_after?: string | null
          refreshed_at?: string | null
          tag?: string | null
          updated_at?: string | null
          user_agent?: string | null
          user_id: string
        }
        Update: {
          aal?: Database["auth"]["Enums"]["aal_level"] | null
          created_at?: string | null
          factor_id?: string | null
          id?: string
          ip?: unknown | null
          not_after?: string | null
          refreshed_at?: string | null
          tag?: string | null
          updated_at?: string | null
          user_agent?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "sessions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      sso_domains: {
        Row: {
          created_at: string | null
          domain: string
          id: string
          sso_provider_id: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          domain: string
          id: string
          sso_provider_id: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          domain?: string
          id?: string
          sso_provider_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sso_domains_sso_provider_id_fkey"
            columns: ["sso_provider_id"]
            isOneToOne: false
            referencedRelation: "sso_providers"
            referencedColumns: ["id"]
          },
        ]
      }
      sso_providers: {
        Row: {
          created_at: string | null
          id: string
          resource_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          id: string
          resource_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          resource_id?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      users: {
        Row: {
          aud: string | null
          banned_until: string | null
          confirmation_sent_at: string | null
          confirmation_token: string | null
          confirmed_at: string | null
          created_at: string | null
          deleted_at: string | null
          email: string | null
          email_change: string | null
          email_change_confirm_status: number | null
          email_change_sent_at: string | null
          email_change_token_current: string | null
          email_change_token_new: string | null
          email_confirmed_at: string | null
          encrypted_password: string | null
          id: string
          instance_id: string | null
          invited_at: string | null
          is_anonymous: boolean
          is_sso_user: boolean
          is_super_admin: boolean | null
          last_sign_in_at: string | null
          phone: string | null
          phone_change: string | null
          phone_change_sent_at: string | null
          phone_change_token: string | null
          phone_confirmed_at: string | null
          raw_app_meta_data: Json | null
          raw_user_meta_data: Json | null
          reauthentication_sent_at: string | null
          reauthentication_token: string | null
          recovery_sent_at: string | null
          recovery_token: string | null
          role: string | null
          updated_at: string | null
        }
        Insert: {
          aud?: string | null
          banned_until?: string | null
          confirmation_sent_at?: string | null
          confirmation_token?: string | null
          confirmed_at?: string | null
          created_at?: string | null
          deleted_at?: string | null
          email?: string | null
          email_change?: string | null
          email_change_confirm_status?: number | null
          email_change_sent_at?: string | null
          email_change_token_current?: string | null
          email_change_token_new?: string | null
          email_confirmed_at?: string | null
          encrypted_password?: string | null
          id: string
          instance_id?: string | null
          invited_at?: string | null
          is_anonymous?: boolean
          is_sso_user?: boolean
          is_super_admin?: boolean | null
          last_sign_in_at?: string | null
          phone?: string | null
          phone_change?: string | null
          phone_change_sent_at?: string | null
          phone_change_token?: string | null
          phone_confirmed_at?: string | null
          raw_app_meta_data?: Json | null
          raw_user_meta_data?: Json | null
          reauthentication_sent_at?: string | null
          reauthentication_token?: string | null
          recovery_sent_at?: string | null
          recovery_token?: string | null
          role?: string | null
          updated_at?: string | null
        }
        Update: {
          aud?: string | null
          banned_until?: string | null
          confirmation_sent_at?: string | null
          confirmation_token?: string | null
          confirmed_at?: string | null
          created_at?: string | null
          deleted_at?: string | null
          email?: string | null
          email_change?: string | null
          email_change_confirm_status?: number | null
          email_change_sent_at?: string | null
          email_change_token_current?: string | null
          email_change_token_new?: string | null
          email_confirmed_at?: string | null
          encrypted_password?: string | null
          id?: string
          instance_id?: string | null
          invited_at?: string | null
          is_anonymous?: boolean
          is_sso_user?: boolean
          is_super_admin?: boolean | null
          last_sign_in_at?: string | null
          phone?: string | null
          phone_change?: string | null
          phone_change_sent_at?: string | null
          phone_change_token?: string | null
          phone_confirmed_at?: string | null
          raw_app_meta_data?: Json | null
          raw_user_meta_data?: Json | null
          reauthentication_sent_at?: string | null
          reauthentication_token?: string | null
          recovery_sent_at?: string | null
          recovery_token?: string | null
          role?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      email: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      jwt: {
        Args: Record<PropertyKey, never>
        Returns: Json
      }
      role: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      uid: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
    }
    Enums: {
      aal_level: "aal1" | "aal2" | "aal3"
      code_challenge_method: "s256" | "plain"
      factor_status: "unverified" | "verified"
      factor_type: "totp" | "webauthn" | "phone"
      one_time_token_type:
        | "confirmation_token"
        | "reauthentication_token"
        | "recovery_token"
        | "email_change_token_new"
        | "email_change_token_current"
        | "phone_change_token"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      lemma: {
        Row: {
          antonyms: Json | null
          commonality: number | null
          created_at: string
          created_by_id: string | null
          cultural_context: string | null
          easily_confused_with: Json | null
          etymology: string | null
          example_usage: Json | null
          guessability: number | null
          id: number
          is_complete: boolean
          language_level: string | null
          lemma: string
          mnemonics: Json | null
          part_of_speech: string
          register: string | null
          related_words_phrases_idioms: Json | null
          synonyms: Json | null
          target_language_code: string
          translations: Json
          updated_at: string
        }
        Insert: {
          antonyms?: Json | null
          commonality?: number | null
          created_at: string
          created_by_id?: string | null
          cultural_context?: string | null
          easily_confused_with?: Json | null
          etymology?: string | null
          example_usage?: Json | null
          guessability?: number | null
          id?: number
          is_complete: boolean
          language_level?: string | null
          lemma: string
          mnemonics?: Json | null
          part_of_speech: string
          register?: string | null
          related_words_phrases_idioms?: Json | null
          synonyms?: Json | null
          target_language_code: string
          translations: Json
          updated_at: string
        }
        Update: {
          antonyms?: Json | null
          commonality?: number | null
          created_at?: string
          created_by_id?: string | null
          cultural_context?: string | null
          easily_confused_with?: Json | null
          etymology?: string | null
          example_usage?: Json | null
          guessability?: number | null
          id?: number
          is_complete?: boolean
          language_level?: string | null
          lemma?: string
          mnemonics?: Json | null
          part_of_speech?: string
          register?: string | null
          related_words_phrases_idioms?: Json | null
          synonyms?: Json | null
          target_language_code?: string
          translations?: Json
          updated_at?: string
        }
        Relationships: []
      }
      lemmaexamplesentence: {
        Row: {
          created_at: string
          id: number
          lemma_id: number
          sentence_id: number
          updated_at: string
        }
        Insert: {
          created_at: string
          id?: number
          lemma_id: number
          sentence_id: number
          updated_at: string
        }
        Update: {
          created_at?: string
          id?: number
          lemma_id?: number
          sentence_id?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "lemmaexamplesentence_lemma_id_fkey"
            columns: ["lemma_id"]
            isOneToOne: false
            referencedRelation: "lemma"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "lemmaexamplesentence_sentence_id_fkey"
            columns: ["sentence_id"]
            isOneToOne: false
            referencedRelation: "sentence"
            referencedColumns: ["id"]
          },
        ]
      }
      migratehistory: {
        Row: {
          id: number
          migrated_at: string
          name: string
        }
        Insert: {
          id?: number
          migrated_at: string
          name: string
        }
        Update: {
          id?: number
          migrated_at?: string
          name?: string
        }
        Relationships: []
      }
      phrase: {
        Row: {
          canonical_form: string
          commonality: number | null
          component_words: Json | null
          created_at: string
          created_by_id: string | null
          cultural_context: string | null
          difficulty_level: string | null
          etymology: string | null
          guessability: number | null
          id: number
          language_level: string | null
          literal_translation: string | null
          mnemonics: Json | null
          part_of_speech: string
          raw_forms: Json
          register: string | null
          slug: string | null
          target_language_code: string
          translations: Json
          updated_at: string
          usage_notes: string | null
        }
        Insert: {
          canonical_form: string
          commonality?: number | null
          component_words?: Json | null
          created_at: string
          created_by_id?: string | null
          cultural_context?: string | null
          difficulty_level?: string | null
          etymology?: string | null
          guessability?: number | null
          id?: number
          language_level?: string | null
          literal_translation?: string | null
          mnemonics?: Json | null
          part_of_speech: string
          raw_forms: Json
          register?: string | null
          slug?: string | null
          target_language_code: string
          translations: Json
          updated_at: string
          usage_notes?: string | null
        }
        Update: {
          canonical_form?: string
          commonality?: number | null
          component_words?: Json | null
          created_at?: string
          created_by_id?: string | null
          cultural_context?: string | null
          difficulty_level?: string | null
          etymology?: string | null
          guessability?: number | null
          id?: number
          language_level?: string | null
          literal_translation?: string | null
          mnemonics?: Json | null
          part_of_speech?: string
          raw_forms?: Json
          register?: string | null
          slug?: string | null
          target_language_code?: string
          translations?: Json
          updated_at?: string
          usage_notes?: string | null
        }
        Relationships: []
      }
      phraseexamplesentence: {
        Row: {
          context: string | null
          created_at: string
          id: number
          phrase_id: number
          sentence_id: number
          updated_at: string
        }
        Insert: {
          context?: string | null
          created_at: string
          id?: number
          phrase_id: number
          sentence_id: number
          updated_at: string
        }
        Update: {
          context?: string | null
          created_at?: string
          id?: number
          phrase_id?: number
          sentence_id?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "phraseexamplesentence_phrase_id_fkey"
            columns: ["phrase_id"]
            isOneToOne: false
            referencedRelation: "phrase"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "phraseexamplesentence_sentence_id_fkey"
            columns: ["sentence_id"]
            isOneToOne: false
            referencedRelation: "sentence"
            referencedColumns: ["id"]
          },
        ]
      }
      profile: {
        Row: {
          created_at: string
          id: number
          target_language_code: string | null
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at: string
          id?: number
          target_language_code?: string | null
          updated_at: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: number
          target_language_code?: string | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      relatedphrase: {
        Row: {
          created_at: string
          from_phrase_id: number
          id: number
          relationship_type: string
          to_phrase_id: number
          updated_at: string
        }
        Insert: {
          created_at: string
          from_phrase_id: number
          id?: number
          relationship_type: string
          to_phrase_id: number
          updated_at: string
        }
        Update: {
          created_at?: string
          from_phrase_id?: number
          id?: number
          relationship_type?: string
          to_phrase_id?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "relatedphrase_from_phrase_id_fkey"
            columns: ["from_phrase_id"]
            isOneToOne: false
            referencedRelation: "phrase"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "relatedphrase_to_phrase_id_fkey"
            columns: ["to_phrase_id"]
            isOneToOne: false
            referencedRelation: "phrase"
            referencedColumns: ["id"]
          },
        ]
      }
      sentence: {
        Row: {
          audio_data: string | null
          created_at: string
          created_by_id: string | null
          id: number
          language_level: string | null
          lemma_words: Json | null
          sentence: string
          slug: string
          target_language_code: string
          translation: string
          updated_at: string
        }
        Insert: {
          audio_data?: string | null
          created_at: string
          created_by_id?: string | null
          id?: number
          language_level?: string | null
          lemma_words?: Json | null
          sentence: string
          slug: string
          target_language_code: string
          translation: string
          updated_at: string
        }
        Update: {
          audio_data?: string | null
          created_at?: string
          created_by_id?: string | null
          id?: number
          language_level?: string | null
          lemma_words?: Json | null
          sentence?: string
          slug?: string
          target_language_code?: string
          translation?: string
          updated_at?: string
        }
        Relationships: []
      }
      sentencelemma: {
        Row: {
          created_at: string
          id: number
          lemma_id: number
          sentence_id: number
          updated_at: string
        }
        Insert: {
          created_at: string
          id?: number
          lemma_id: number
          sentence_id: number
          updated_at: string
        }
        Update: {
          created_at?: string
          id?: number
          lemma_id?: number
          sentence_id?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sentencelemma_lemma_id_fkey"
            columns: ["lemma_id"]
            isOneToOne: false
            referencedRelation: "lemma"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "sentencelemma_sentence_id_fkey"
            columns: ["sentence_id"]
            isOneToOne: false
            referencedRelation: "sentence"
            referencedColumns: ["id"]
          },
        ]
      }
      sourcedir: {
        Row: {
          created_at: string
          created_by_id: string | null
          description: string | null
          id: number
          path: string
          slug: string
          target_language_code: string
          updated_at: string
        }
        Insert: {
          created_at: string
          created_by_id?: string | null
          description?: string | null
          id?: number
          path: string
          slug: string
          target_language_code: string
          updated_at: string
        }
        Update: {
          created_at?: string
          created_by_id?: string | null
          description?: string | null
          id?: number
          path?: string
          slug?: string
          target_language_code?: string
          updated_at?: string
        }
        Relationships: []
      }
      sourcefile: {
        Row: {
          ai_generated: boolean
          audio_data: string | null
          audio_filename: string | null
          created_at: string
          created_by_id: string | null
          description: string | null
          filename: string
          id: number
          image_data: string | null
          language_level: string | null
          metadata: Json
          num_words: number | null
          publication_date: string | null
          slug: string
          sourcedir_id: number
          sourcefile_type: string
          text_english: string
          text_target: string
          title_target: string | null
          updated_at: string
          url: string | null
        }
        Insert: {
          ai_generated: boolean
          audio_data?: string | null
          audio_filename?: string | null
          created_at: string
          created_by_id?: string | null
          description?: string | null
          filename: string
          id?: number
          image_data?: string | null
          language_level?: string | null
          metadata: Json
          num_words?: number | null
          publication_date?: string | null
          slug: string
          sourcedir_id: number
          sourcefile_type: string
          text_english: string
          text_target: string
          title_target?: string | null
          updated_at: string
          url?: string | null
        }
        Update: {
          ai_generated?: boolean
          audio_data?: string | null
          audio_filename?: string | null
          created_at?: string
          created_by_id?: string | null
          description?: string | null
          filename?: string
          id?: number
          image_data?: string | null
          language_level?: string | null
          metadata?: Json
          num_words?: number | null
          publication_date?: string | null
          slug?: string
          sourcedir_id?: number
          sourcefile_type?: string
          text_english?: string
          text_target?: string
          title_target?: string | null
          updated_at?: string
          url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sourcefile_sourcedir_id_fkey"
            columns: ["sourcedir_id"]
            isOneToOne: false
            referencedRelation: "sourcedir"
            referencedColumns: ["id"]
          },
        ]
      }
      sourcefilephrase: {
        Row: {
          centrality: number | null
          created_at: string
          id: number
          ordering: number | null
          phrase_id: number
          sourcefile_id: number
          updated_at: string
        }
        Insert: {
          centrality?: number | null
          created_at: string
          id?: number
          ordering?: number | null
          phrase_id: number
          sourcefile_id: number
          updated_at: string
        }
        Update: {
          centrality?: number | null
          created_at?: string
          id?: number
          ordering?: number | null
          phrase_id?: number
          sourcefile_id?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sourcefilephrase_phrase_id_fkey"
            columns: ["phrase_id"]
            isOneToOne: false
            referencedRelation: "phrase"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "sourcefilephrase_sourcefile_id_fkey"
            columns: ["sourcefile_id"]
            isOneToOne: false
            referencedRelation: "sourcefile"
            referencedColumns: ["id"]
          },
        ]
      }
      sourcefilewordform: {
        Row: {
          centrality: number | null
          created_at: string
          id: number
          ordering: number | null
          sourcefile_id: number
          updated_at: string
          wordform_id: number
        }
        Insert: {
          centrality?: number | null
          created_at: string
          id?: number
          ordering?: number | null
          sourcefile_id: number
          updated_at: string
          wordform_id: number
        }
        Update: {
          centrality?: number | null
          created_at?: string
          id?: number
          ordering?: number | null
          sourcefile_id?: number
          updated_at?: string
          wordform_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "sourcefilewordform_sourcefile_id_fkey"
            columns: ["sourcefile_id"]
            isOneToOne: false
            referencedRelation: "sourcefile"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "sourcefilewordform_wordform_id_fkey"
            columns: ["wordform_id"]
            isOneToOne: false
            referencedRelation: "wordform"
            referencedColumns: ["id"]
          },
        ]
      }
      test_model: {
        Row: {
          id: number
          name: string
        }
        Insert: {
          id?: number
          name: string
        }
        Update: {
          id?: number
          name?: string
        }
        Relationships: []
      }
      userlemma: {
        Row: {
          created_at: string
          id: number
          ignored_dt: string | null
          lemma_id: number
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at: string
          id?: number
          ignored_dt?: string | null
          lemma_id: number
          updated_at: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: number
          ignored_dt?: string | null
          lemma_id?: number
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "userlemma_lemma_id_fkey"
            columns: ["lemma_id"]
            isOneToOne: false
            referencedRelation: "lemma"
            referencedColumns: ["id"]
          },
        ]
      }
      wordform: {
        Row: {
          created_at: string
          created_by_id: string | null
          id: number
          inflection_type: string | null
          is_lemma: boolean
          lemma_entry_id: number | null
          part_of_speech: string | null
          possible_misspellings: Json | null
          target_language_code: string
          translations: Json | null
          updated_at: string
          wordform: string | null
        }
        Insert: {
          created_at: string
          created_by_id?: string | null
          id?: number
          inflection_type?: string | null
          is_lemma: boolean
          lemma_entry_id?: number | null
          part_of_speech?: string | null
          possible_misspellings?: Json | null
          target_language_code: string
          translations?: Json | null
          updated_at: string
          wordform?: string | null
        }
        Update: {
          created_at?: string
          created_by_id?: string | null
          id?: number
          inflection_type?: string | null
          is_lemma?: boolean
          lemma_entry_id?: number | null
          part_of_speech?: string | null
          possible_misspellings?: Json | null
          target_language_code?: string
          translations?: Json | null
          updated_at?: string
          wordform?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "wordform_lemma_entry_id_fkey"
            columns: ["lemma_entry_id"]
            isOneToOne: false
            referencedRelation: "lemma"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  auth: {
    Enums: {
      aal_level: ["aal1", "aal2", "aal3"],
      code_challenge_method: ["s256", "plain"],
      factor_status: ["unverified", "verified"],
      factor_type: ["totp", "webauthn", "phone"],
      one_time_token_type: [
        "confirmation_token",
        "reauthentication_token",
        "recovery_token",
        "email_change_token_new",
        "email_change_token_current",
        "phone_change_token",
      ],
    },
  },
  public: {
    Enums: {},
  },
} as const

