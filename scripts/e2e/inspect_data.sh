#!/usr/bin/env bash
# ============================================================================
# inspect_data.sh — Show current state of the agentic_math_tutor data service
#
# Queries both PostgreSQL and Neo4j to display:
#   - PostgreSQL: videos table summary + recent rows
#   - Neo4j: Concept nodes, Video nodes, PREREQUISITE and DEMONSTRATES edges
#
# Usage:
#   ./scripts/e2e/inspect_data.sh            # show all
#   ./scripts/e2e/inspect_data.sh pg         # PostgreSQL only
#   ./scripts/e2e/inspect_data.sh neo4j      # Neo4j only
# ============================================================================
set -euo pipefail

# --- Configuration (override via env vars) ---
PG_CONTAINER="${PG_CONTAINER:-math_tutor_postgres}"
PG_USER="${PG_USER:-math_tutor_app}"
PG_DB="${PG_DB:-math_tutor}"

NEO4J_CONTAINER="${NEO4J_CONTAINER:-math_tutor_neo4j}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-local_dev_password}"

SECTION="${1:-all}"   # all | pg | neo4j

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

pg_query() {
    docker exec -i "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB" -c "$1"
}

neo4j_query() {
    docker exec -i "$NEO4J_CONTAINER" cypher-shell \
        -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "$1"
}

# ============================================================================
# PostgreSQL
# ============================================================================
show_pg() {
    echo ""
    echo -e "${BLUE}${BOLD}================================================================${NC}"
    echo -e "${BLUE}${BOLD}  PostgreSQL  (${PG_CONTAINER})${NC}"
    echo -e "${BLUE}${BOLD}================================================================${NC}"

    echo ""
    echo -e "${GREEN}--- Tables ---${NC}"
    pg_query "\dt"

    echo ""
    echo -e "${GREEN}--- Videos: count by source ---${NC}"
    pg_query "SELECT source, count(*) AS cnt FROM videos GROUP BY source ORDER BY cnt DESC;"

    echo ""
    echo -e "${GREEN}--- Videos: count by status ---${NC}"
    pg_query "SELECT status, count(*) AS cnt FROM videos GROUP BY status ORDER BY cnt DESC;"

    echo ""
    echo -e "${GREEN}--- Videos: count by (concept_id, theme) ---${NC}"
    pg_query "SELECT concept_id, theme, count(*) AS cnt FROM videos GROUP BY concept_id, theme ORDER BY concept_id, theme;"

    echo ""
    echo -e "${GREEN}--- Videos: 20 most recent rows ---${NC}"
    pg_query "
        SELECT
            concept_id,
            theme,
            grade,
            status,
            source,
            engine_video_id,
            file_size_bytes,
            generation_time_seconds,
            error_message,
            created_at::text
        FROM videos
        ORDER BY created_at DESC
        LIMIT 20;
    "

    echo ""
    echo -e "${GREEN}--- Students ---${NC}"
    pg_query "SELECT count(*) AS student_count FROM students;"

    echo ""
    echo -e "${GREEN}--- Student Sessions ---${NC}"
    pg_query "SELECT count(*) AS session_count FROM student_sessions;"
}

# ============================================================================
# Neo4j
# ============================================================================
show_neo4j() {
    echo ""
    echo -e "${CYAN}${BOLD}================================================================${NC}"
    echo -e "${CYAN}${BOLD}  Neo4j  (${NEO4J_CONTAINER})${NC}"
    echo -e "${CYAN}${BOLD}================================================================${NC}"

    echo ""
    echo -e "${YELLOW}--- Node counts by label ---${NC}"
    neo4j_query "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS cnt ORDER BY cnt DESC;"

    echo ""
    echo -e "${YELLOW}--- Relationship counts by type ---${NC}"
    neo4j_query "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(*) AS cnt ORDER BY cnt DESC;"

    echo ""
    echo -e "${YELLOW}--- Concepts: categories ---${NC}"
    neo4j_query "MATCH (c:Concept) RETURN c.category AS category, count(*) AS cnt ORDER BY cnt DESC;"

    echo ""
    echo -e "${YELLOW}--- Concepts: sample (first 10) ---${NC}"
    neo4j_query "
        MATCH (c:Concept)
        RETURN c.concept_id AS concept_id,
               c.name AS name,
               c.category AS category,
               c.difficulty AS difficulty
        ORDER BY c.concept_id
        LIMIT 10;
    "

    echo ""
    echo -e "${YELLOW}--- PREREQUISITE edges: sample (first 10) ---${NC}"
    neo4j_query "
        MATCH (a:Concept)-[r:PREREQUISITE]->(b:Concept)
        RETURN a.concept_id AS from_concept,
               b.concept_id AS to_concept,
               r.strength AS strength
        ORDER BY a.concept_id
        LIMIT 10;
    "

    echo ""
    echo -e "${YELLOW}--- Video nodes: count by source ---${NC}"
    neo4j_query "MATCH (v:Video) RETURN v.source AS source, count(*) AS cnt ORDER BY cnt DESC;"

    echo ""
    echo -e "${YELLOW}--- Video nodes: count by status ---${NC}"
    neo4j_query "MATCH (v:Video) RETURN v.status AS status, count(*) AS cnt ORDER BY cnt DESC;"

    echo ""
    echo -e "${YELLOW}--- DEMONSTRATES edges: Video -> Concept (20 most recent) ---${NC}"
    neo4j_query "
        MATCH (v:Video)-[r:DEMONSTRATES]->(c:Concept)
        RETURN v.engine_video_id AS engine_video_id,
               v.concept_id AS video_concept,
               v.theme AS theme,
               v.grade AS grade,
               v.status AS status,
               v.source AS source,
               c.concept_id AS linked_concept,
               r.is_primary AS is_primary,
               r.demonstration_type AS demo_type
        ORDER BY v.created_at DESC
        LIMIT 20;
    "

    echo ""
    echo -e "${YELLOW}--- Concepts with most DEMONSTRATES edges ---${NC}"
    neo4j_query "
        MATCH (c:Concept)<-[r:DEMONSTRATES]-(v:Video)
        RETURN c.concept_id AS concept_id,
               c.name AS name,
               count(v) AS video_count
        ORDER BY video_count DESC
        LIMIT 10;
    "

    echo ""
    echo -e "${YELLOW}--- Orphan Video nodes (no DEMONSTRATES edge) ---${NC}"
    neo4j_query "
        MATCH (v:Video)
        WHERE NOT (v)-[:DEMONSTRATES]->()
        RETURN v.engine_video_id AS engine_video_id,
               v.concept_id AS concept_id,
               v.source AS source
        LIMIT 10;
    "
}

# ============================================================================
# Main
# ============================================================================
case "$SECTION" in
    pg)       show_pg ;;
    neo4j)    show_neo4j ;;
    all)      show_pg; show_neo4j ;;
    *)
        echo "Usage: $0 [all|pg|neo4j]"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}Done.${NC}"
