package com.deloitte.lumens.observability;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/** Factory methods for bounded source-level attribute policies. */
public final class LumensAttributePolicies {
    private static final Set<String> FORBIDDEN_KEY_PARTS = Set.of(
            "authorization", "cookie", "credential", "password", "secret", "token");

    private LumensAttributePolicies() {}

    /**
     * Retains only registered keys and drops names that obviously imply credentials.
     * Contract-driven policies can replace this default in a later runtime integration.
     */
    public static LumensAttributePolicy registeredKeys(Set<String> registeredKeys) {
        Set<String> allowed = Set.copyOf(registeredKeys);
        return attributes -> {
            Map<String, String> accepted = new LinkedHashMap<>();
            for (Map.Entry<String, String> entry : attributes.entrySet()) {
                String key = entry.getKey();
                if (allowed.contains(key) && !isForbidden(key) && entry.getValue() != null) {
                    accepted.put(key, entry.getValue());
                }
            }
            return Map.copyOf(accepted);
        };
    }

    /** Drops all custom attributes; safe for applications without a loaded contract. */
    public static LumensAttributePolicy denyAll() {
        return ignored -> Map.of();
    }

    private static boolean isForbidden(String key) {
        String lowercase = key.toLowerCase();
        return FORBIDDEN_KEY_PARTS.stream().anyMatch(lowercase::contains);
    }
}
