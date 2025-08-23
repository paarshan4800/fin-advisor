import React, { useState } from 'react'
import api from '../../api'
import { useUser } from '../../context/UserContext'

function useTransactions() {

    const [transactionsData, settransactionsData] = useState([])
    const [transactionsLoading, settransactionsLoading] = useState(false)
    const [transactionsError, settransactionsError] = useState(null)

    const TRANSACTIONS_URI = "/transactions"

    const { userId } = useUser()  

    const fetchTransactions = async (
        pageNumber = 1,
        pageSize = 10,
    ) => {

        settransactionsLoading(true);

        try {
            const payload = {
                "pageNumber": pageNumber,
                "pageSize": pageSize,
                "userId": userId
            }
            const resp = await api.post(TRANSACTIONS_URI, payload);
            console.log(resp);

            if ("data" in resp.data) {
                settransactionsData(resp.data.data);
            } else {
                throw Error("error")
            }

        } catch (e) {
            settransactionsError(e.message)
        } finally {
            settransactionsLoading(false)
        }

    }

    return {
        fetchTransactions,
        transactionsData,
        transactionsLoading,
        transactionsError
    }
}

export default useTransactions