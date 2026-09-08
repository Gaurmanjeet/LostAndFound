const API_URL = "http://127.0.0.1:5000";


function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


async function apiRequest(endpoint, options = {}) {

    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            credentials: "include",
            ...options
        }
    );


    let data;

    try {

        data = await response.json();

    } catch (error) {

        throw new Error(
            `Server returned invalid response (${response.status})`
        );

    }


    if (!response.ok) {

        throw new Error(
            data.message ||
            `Request failed (${response.status})`
        );

    }


    return data;
}


// ======================================================
// LOGOUT
// ======================================================

async function adminLogout() {

    try {

        await apiRequest(
            "/api/logout",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error(error);

    }


    window.location.href =
        "index.html";
}


window.adminLogout =
    adminLogout;


// ======================================================
// SET TEXT
// ======================================================

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value ?? 0;

    }
}


// ======================================================
// LOAD ADMIN DASHBOARD
// ======================================================

async function loadAdminDashboard() {

    try {

        const result =
            await apiRequest(
                "/api/admin/dashboard"
            );


        const stats =
            result.stats || {};


        setText(
            "totalUsers",
            stats.total_users
        );


        setText(
            "totalItems",
            stats.total_items
        );


        setText(
            "lostItems",
            stats.lost_items
        );


        setText(
            "foundItems",
            stats.found_items
        );


        setText(
            "activeItems",
            stats.active_items
        );


        setText(
            "returnedItems",
            stats.returned_items
        );


        setText(
            "pendingClaims",
            stats.pending_claims
        );


        setText(
            "approvedClaims",
            stats.approved_claims
        );


        setText(
            "rejectedClaims",
            stats.rejected_claims
        );


        setText(
            "totalMatches",
            stats.total_matches
        );


        await loadClaims();


    } catch (error) {

        console.error(
            "Admin dashboard error:",
            error
        );

        alert(error.message);

    }

}


// ======================================================
// LOAD CLAIMS
// ======================================================

async function loadClaims() {

    const container =
        document.getElementById(
            "adminClaimsContainer"
        );


    if (!container) {
        return;
    }


    try {

        const result =
            await apiRequest(
                "/api/admin/claims"
            );


        const claims =
            result.claims || [];


        if (claims.length === 0) {

            container.innerHTML = `
                <div class="text-center py-5">

                    <i
                        class="fa-solid fa-inbox fa-3x text-muted"
                    ></i>

                    <p class="mt-3 text-muted">
                        No claim requests found.
                    </p>

                </div>
            `;

            return;
        }


        container.innerHTML =
            claims
                .map(renderClaim)
                .join("");


    } catch (error) {

        console.error(
            "Claims error:",
            error
        );


        container.innerHTML = `
            <div class="alert alert-danger">

                Failed to load claim requests.

                <br>

                <small>
                    ${escapeHTML(error.message)}
                </small>

            </div>
        `;

    }

}


// ======================================================
// RENDER CLAIM
// ======================================================

function renderClaim(claim) {

    // Support both old and new backend names
    const claimId =
        claim.id ??
        claim.claim_id;


    const status =
        claim.status ??
        claim.claim_status ??
        "pending";


    const itemTitle =
        claim.item_title ||
        "Unknown item";


    const claimant =
        claim.claimant_name ||
        "Unknown user";


    const description =
        claim.claim_description ||
        "No description provided.";


    const isPending =
        status.toLowerCase() === "pending";


    return `

        <div
            class="border rounded p-4 mb-3 shadow-sm"
            id="claim-${claimId}"
        >

            <div
                class="d-flex justify-content-between align-items-start gap-3"
            >

                <div class="flex-grow-1">

                    <h5 class="mb-2">
                        ${escapeHTML(itemTitle)}
                    </h5>


                    <p class="mb-2">

                        <strong>
                            Claimant:
                        </strong>

                        ${escapeHTML(claimant)}

                    </p>


                    <p class="mb-2">

                        <strong>
                            Description:
                        </strong>

                        ${escapeHTML(description)}

                    </p>


                    <span
                        class="badge ${
                            status === "pending"
                                ? "text-bg-warning"
                                : status === "approved"
                                    ? "text-bg-success"
                                    : "text-bg-danger"
                        }"
                    >
                        ${escapeHTML(status)}
                    </span>

                </div>


                ${
                    isPending
                        ? `

                            <div
                                class="d-flex flex-column gap-2"
                                style="min-width:120px;"
                            >

                                <button
                                    type="button"
                                    class="btn btn-success btn-sm"
                                    onclick="approveClaim(${claimId})"
                                >

                                    <i
                                        class="fa-solid fa-check me-1"
                                    ></i>

                                    Approve

                                </button>


                                <button
                                    type="button"
                                    class="btn btn-danger btn-sm"
                                    onclick="rejectClaim(${claimId})"
                                >

                                    <i
                                        class="fa-solid fa-xmark me-1"
                                    ></i>

                                    Reject

                                </button>

                            </div>

                          `
                        : ""
                }

            </div>

        </div>

    `;
}


// ======================================================
// APPROVE CLAIM
// ======================================================

async function approveClaim(claimId) {

    const confirmed =
        confirm(
            "Are you sure you want to approve this claim?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const result =
            await apiRequest(
                `/api/admin/claims/${claimId}/approve`,
                {
                    method: "POST"
                }
            );


        alert(
            result.message ||
            "Claim approved."
        );


        await loadAdminDashboard();


    } catch (error) {

        console.error(
            "Approve error:",
            error
        );


        alert(
            error.message
        );

    }

}


window.approveClaim =
    approveClaim;


// ======================================================
// REJECT CLAIM
// ======================================================

async function rejectClaim(claimId) {

    const confirmed =
        confirm(
            "Are you sure you want to reject this claim?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const result =
            await apiRequest(
                `/api/admin/claims/${claimId}/reject`,
                {
                    method: "POST"
                }
            );


        alert(
            result.message ||
            "Claim rejected."
        );


        await loadAdminDashboard();


    } catch (error) {

        console.error(
            "Reject error:",
            error
        );


        alert(
            error.message
        );

    }

}


window.rejectClaim =
    rejectClaim;


// ======================================================
// INITIALIZE
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadAdminDashboard();

    }
);